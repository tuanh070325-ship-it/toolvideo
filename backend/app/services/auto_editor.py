"""
Auto-Editor Service - Smart video editing automation
Inspired by WyattBlue/auto-editor

Features:
- Automatic silence detection and removal
- Speed adjustment for non-speech segments
- Smart video trimming based on audio analysis
- Multi-track audio handling
"""

import asyncio
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import uuid

from app.core.logger import logger
from app.core.config import settings


class AutoEditorService:
    """Service for automatic video editing and silence removal"""
    
    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.PROCESSED_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def analyze_audio_levels(
        self, 
        video_path: Path,
        threshold_db: float = -30.0,
        min_silence_duration: float = 0.3
    ) -> Dict[str, Any]:
        """
        Analyze video audio to detect speech and silence segments
        
        Args:
            video_path: Path to input video
            threshold_db: Silence threshold in dB (default -30dB)
            min_silence_duration: Minimum silence duration to detect (seconds)
            
        Returns:
            Dict with speech and silence segments
        """
        try:
            logger.info(f"Analyzing audio levels: {video_path}")
            
            # Use FFmpeg to analyze audio
            # Extract audio and analyze with silencedetect filter
            cmd = [
                "ffmpeg", "-i", str(video_path),
                "-af", f"silencedetect=noise={threshold_db}dB:d={min_silence_duration}",
                "-f", "null", "-"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _, stderr = await process.communicate()
            
            # Parse silence detection output
            output = stderr.decode('utf-8', errors='ignore')
            silences = self._parse_silence_output(output)
            
            # Get video duration
            duration = await self._get_video_duration(video_path)
            
            # Calculate speech segments (inverse of silence)
            speech_segments = self._calculate_speech_segments(silences, duration)
            
            total_silence = sum(s['duration'] for s in silences)
            total_speech = sum(s['duration'] for s in speech_segments)
            
            return {
                "success": True,
                "duration": duration,
                "silences": silences,
                "speech_segments": speech_segments,
                "total_silence_seconds": total_silence,
                "total_speech_seconds": total_speech,
                "silence_percentage": (total_silence / duration * 100) if duration > 0 else 0,
                "speech_percentage": (total_speech / duration * 100) if duration > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _parse_silence_output(self, output: str) -> List[Dict[str, float]]:
        """Parse FFmpeg silencedetect output"""
        silences = []
        current_silence = {}
        
        for line in output.split('\n'):
            if 'silence_start:' in line:
                try:
                    start = float(line.split('silence_start:')[1].strip().split()[0])
                    current_silence['start'] = start
                except (ValueError, IndexError):
                    pass
                    
            elif 'silence_end:' in line and 'silence_duration:' in line:
                try:
                    parts = line.split('silence_end:')[1].strip()
                    end = float(parts.split()[0])
                    duration = float(line.split('silence_duration:')[1].strip())
                    
                    if 'start' in current_silence:
                        silences.append({
                            'start': current_silence['start'],
                            'end': end,
                            'duration': duration
                        })
                    current_silence = {}
                except (ValueError, IndexError):
                    pass
        
        return silences
    
    def _calculate_speech_segments(
        self, 
        silences: List[Dict[str, float]], 
        total_duration: float
    ) -> List[Dict[str, float]]:
        """Calculate speech segments from silence gaps"""
        if not silences:
            return [{'start': 0, 'end': total_duration, 'duration': total_duration}]
        
        speech_segments = []
        current_pos = 0
        
        for silence in sorted(silences, key=lambda x: x['start']):
            if silence['start'] > current_pos:
                speech_segments.append({
                    'start': current_pos,
                    'end': silence['start'],
                    'duration': silence['start'] - current_pos
                })
            current_pos = silence['end']
        
        # Add final segment if needed
        if current_pos < total_duration:
            speech_segments.append({
                'start': current_pos,
                'end': total_duration,
                'duration': total_duration - current_pos
            })
        
        return speech_segments
    
    async def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration using FFprobe"""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "json", str(video_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await process.communicate()
        
        try:
            data = json.loads(stdout.decode())
            return float(data['format']['duration'])
        except (json.JSONDecodeError, KeyError, ValueError):
            return 0.0
    
    async def remove_silence(
        self,
        video_path: Path,
        output_path: Optional[Path] = None,
        threshold_db: float = -30.0,
        min_silence_duration: float = 0.5,
        margin: float = 0.1,
        speed_up_silence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Remove silence from video or speed up silent sections
        
        Args:
            video_path: Input video path
            output_path: Output path (optional, auto-generated if not provided)
            threshold_db: Silence threshold in dB
            min_silence_duration: Minimum silence to consider (seconds)
            margin: Keep margin around speech (seconds)
            speed_up_silence: If set, speed up silence instead of removing (e.g., 4.0 = 4x speed)
            
        Returns:
            Dict with result info
        """
        try:
            job_id = str(uuid.uuid4())[:8]
            output_path = output_path or self.output_dir / f"auto_edit_{job_id}.mp4"
            
            logger.info(f"Removing silence from video: {video_path}")
            
            # First analyze the audio
            analysis = await self.analyze_audio_levels(
                video_path, threshold_db, min_silence_duration
            )
            
            if not analysis.get('success'):
                return analysis
            
            speech_segments = analysis['speech_segments']
            
            if not speech_segments:
                return {"success": False, "error": "No speech segments found"}
            
            # Add margin to segments
            speech_segments = [
                {
                    'start': max(0, seg['start'] - margin),
                    'end': min(analysis['duration'], seg['end'] + margin),
                    'duration': seg['duration'] + 2 * margin
                }
                for seg in speech_segments
            ]
            
            # Merge overlapping segments
            speech_segments = self._merge_overlapping_segments(speech_segments)
            
            if speed_up_silence:
                # Speed up silent parts instead of removing them
                result = await self._speed_up_silent_sections(
                    video_path, output_path, speech_segments, 
                    analysis['silences'], speed_up_silence, analysis['duration']
                )
            else:
                # Cut out silence completely
                result = await self._cut_segments(video_path, output_path, speech_segments)
            
            if result.get('success'):
                new_duration = await self._get_video_duration(output_path)
                result.update({
                    "original_duration": analysis['duration'],
                    "new_duration": new_duration,
                    "time_saved": analysis['duration'] - new_duration,
                    "reduction_percentage": (1 - new_duration / analysis['duration']) * 100 if analysis['duration'] > 0 else 0
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Remove silence failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _merge_overlapping_segments(
        self, 
        segments: List[Dict[str, float]]
    ) -> List[Dict[str, float]]:
        """Merge overlapping segments"""
        if not segments:
            return []
        
        sorted_segments = sorted(segments, key=lambda x: x['start'])
        merged = [sorted_segments[0]]
        
        for seg in sorted_segments[1:]:
            if seg['start'] <= merged[-1]['end']:
                merged[-1]['end'] = max(merged[-1]['end'], seg['end'])
                merged[-1]['duration'] = merged[-1]['end'] - merged[-1]['start']
            else:
                merged.append(seg)
        
        return merged
    
    async def _cut_segments(
        self, 
        video_path: Path, 
        output_path: Path,
        segments: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """Cut video to keep only specified segments"""
        try:
            # Create filter complex for segment extraction
            temp_parts = []
            filter_parts = []
            
            for i, seg in enumerate(segments):
                temp_file = self.temp_dir / f"seg_{str(uuid.uuid4())[:8]}_{i}.mp4"
                temp_parts.append(temp_file)
                
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(video_path),
                    "-ss", str(seg['start']),
                    "-t", str(seg['duration']),
                    "-c:v", "libx264", "-preset", "fast",
                    "-c:a", "aac",
                    str(temp_file)
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
            
            # Concatenate segments
            if len(temp_parts) == 1:
                # Just rename the single segment
                temp_parts[0].rename(output_path)
            else:
                # Create concat file
                concat_file = self.temp_dir / f"concat_{str(uuid.uuid4())[:8]}.txt"
                with open(concat_file, 'w') as f:
                    for part in temp_parts:
                        f.write(f"file '{part}'\n")
                
                cmd = [
                    "ffmpeg", "-y",
                    "-f", "concat", "-safe", "0",
                    "-i", str(concat_file),
                    "-c", "copy",
                    str(output_path)
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                # Cleanup
                concat_file.unlink(missing_ok=True)
                for part in temp_parts:
                    part.unlink(missing_ok=True)
            
            return {
                "success": True,
                "output_path": str(output_path),
                "segments_used": len(segments)
            }
            
        except Exception as e:
            logger.error(f"Cut segments failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _speed_up_silent_sections(
        self,
        video_path: Path,
        output_path: Path,
        speech_segments: List[Dict[str, float]],
        silence_segments: List[Dict[str, float]],
        speed_factor: float,
        total_duration: float
    ) -> Dict[str, Any]:
        """Speed up silent sections while keeping speech at normal speed"""
        try:
            # Build complex filter for variable speed
            temp_parts = []
            all_segments = []
            
            # Combine speech and silence segments with type markers
            for seg in speech_segments:
                all_segments.append({**seg, 'type': 'speech'})
            for seg in silence_segments:
                all_segments.append({**seg, 'type': 'silence'})
            
            all_segments.sort(key=lambda x: x['start'])
            
            # Process each segment
            for i, seg in enumerate(all_segments):
                temp_file = self.temp_dir / f"speed_seg_{str(uuid.uuid4())[:8]}_{i}.mp4"
                temp_parts.append(temp_file)
                
                if seg['type'] == 'silence' and seg['duration'] > 0.1:
                    # Speed up silence
                    cmd = [
                        "ffmpeg", "-y",
                        "-i", str(video_path),
                        "-ss", str(seg['start']),
                        "-t", str(seg['duration']),
                        "-filter_complex",
                        f"[0:v]setpts=PTS/{speed_factor}[v];[0:a]atempo={min(speed_factor, 2.0)}[a]",
                        "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "fast",
                        str(temp_file)
                    ]
                else:
                    # Keep speech at normal speed
                    cmd = [
                        "ffmpeg", "-y",
                        "-i", str(video_path),
                        "-ss", str(seg['start']),
                        "-t", str(seg['duration']),
                        "-c:v", "libx264", "-preset", "fast",
                        "-c:a", "aac",
                        str(temp_file)
                    ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
            
            # Filter out empty files
            temp_parts = [p for p in temp_parts if p.exists() and p.stat().st_size > 0]
            
            if not temp_parts:
                return {"success": False, "error": "No valid segments created"}
            
            # Concatenate
            concat_file = self.temp_dir / f"concat_{str(uuid.uuid4())[:8]}.txt"
            with open(concat_file, 'w') as f:
                for part in temp_parts:
                    f.write(f"file '{part}'\n")
            
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c", "copy",
                str(output_path)
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            # Cleanup
            concat_file.unlink(missing_ok=True)
            for part in temp_parts:
                part.unlink(missing_ok=True)
            
            return {
                "success": True,
                "output_path": str(output_path),
                "speed_factor": speed_factor
            }
            
        except Exception as e:
            logger.error(f"Speed up silent sections failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def smart_trim(
        self,
        video_path: Path,
        target_duration: int,
        output_path: Optional[Path] = None,
        keep_start: bool = True,
        keep_end: bool = True
    ) -> Dict[str, Any]:
        """
        Smart trim video to target duration while preserving important content
        
        Args:
            video_path: Input video path
            target_duration: Target duration in seconds
            output_path: Output path (optional)
            keep_start: Always keep beginning
            keep_end: Always keep ending
            
        Returns:
            Dict with result info
        """
        try:
            job_id = str(uuid.uuid4())[:8]
            output_path = output_path or self.output_dir / f"smart_trim_{job_id}.mp4"
            
            # Analyze audio to find best segments
            analysis = await self.analyze_audio_levels(video_path)
            
            if not analysis.get('success'):
                return analysis
            
            original_duration = analysis['duration']
            
            if original_duration <= target_duration:
                # No trimming needed
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(video_path),
                    "-c", "copy",
                    str(output_path)
                ]
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await process.communicate()
                
                return {
                    "success": True,
                    "output_path": str(output_path),
                    "original_duration": original_duration,
                    "new_duration": original_duration,
                    "trimmed": False
                }
            
            # Select best segments to keep
            speech_segments = analysis['speech_segments']
            
            # Prioritize segments with more speech content
            segments_to_keep = []
            current_duration = 0
            
            # Always keep start
            if keep_start and speech_segments:
                start_seg = speech_segments[0]
                segments_to_keep.append(start_seg)
                current_duration += start_seg['duration']
            
            # Add middle segments until we reach target
            for seg in speech_segments[1:-1]:
                if current_duration + seg['duration'] <= target_duration:
                    segments_to_keep.append(seg)
                    current_duration += seg['duration']
            
            # Always keep end
            if keep_end and len(speech_segments) > 1:
                end_seg = speech_segments[-1]
                if current_duration + end_seg['duration'] <= target_duration * 1.1:
                    segments_to_keep.append(end_seg)
            
            # Cut and join segments
            result = await self._cut_segments(video_path, output_path, segments_to_keep)
            
            if result.get('success'):
                new_duration = await self._get_video_duration(output_path)
                result.update({
                    "original_duration": original_duration,
                    "new_duration": new_duration,
                    "trimmed": True,
                    "segments_kept": len(segments_to_keep)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Smart trim failed: {e}")
            return {"success": False, "error": str(e)}


# Global instance
auto_editor = AutoEditorService()
