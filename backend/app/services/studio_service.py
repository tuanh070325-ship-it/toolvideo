import json
import logging
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.services.ai.story_generator import get_story_generator
from app.services.ai.image_generator import get_image_generator
from app.services.ai.tts_provider import get_tts_provider
from app.services.studio.character_profiles import get_character_base_prompt
from app.core.quotas import quota_manager
import shutil
import zipfile
import httpx

logger = logging.getLogger(__name__)

class StudioService:
    """Service for Story Studio (KOC Studio) features"""
    
    def __init__(self):
        self.ai_provider = settings.AI_PROVIDER
        
    async def generate_ideas(self, topic: str) -> List[Dict[str, Any]]:
        """Generate 5 viral story ideas based on a topic"""
        logger.info(f"Generating ideas for topic: {topic}")
        
        # Check quota
        if not quota_manager.check_quota("gemini", 1): # Using 1 request as cost
            logger.warning("Quota exceeded for idea generation")
            # Fallback to some basic ideas if needed, or raise
            raise Exception("API Quota exceeded")

        story_gen = await get_story_generator(self.ai_provider)
        
        prompt = f"""Bạn là một đạo diễn sáng tạo nội dung bậc thầy trên TikTok và Youtube Shorts, chuyên tạo ra những video hàng triệu view.
Chủ đề là: "{topic}"

Hãy tạo ra 5 ý tưởng (hook) video ĐỘC ĐÁO và DỄ GÂY BÃO. Đừng làm theo phong cách kể chuyện truyền thống, hãy sử dụng các kỹ thuật như:
- Sự thật gây sốc (Shocking Truth)
- Lầm tưởng phổ biến (Common Myths)
- Kết quả điên rồ (Insane Results)
- Câu chuyện kịch tính (Dramatic Story)
- Sự hài hước bất ngờ (Surprise Humor)

Mỗi ý tưởng cần có:
1. Title: Tiêu đề cực bốc, kích thích sự tò mò ngay lập tức.
2. Description: Mô tả cách quay cảnh đầu tiên (cảnh hook) để giữ chân người xem trong 3 giây đầu.
3. Style: (Lựa chọn: Hài hước, Kịch tính, Kinh dị, Mẹo vặt thông minh, Cảm động).

Trả về kết quả dưới dạng JSON array:
[
  {{"id": "1", "title": "...", "description": "...", "style": "..."}},
  ...
]
Chỉ trả về JSON, không giải thích gì thêm. Ngôn ngữ: Tiếng Việt."""

        try:
            response_text = await story_gen.generate_story(prompt, max_length=1000)
            
            # Clean JSON response if AI adds markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
                
            ideas = json.loads(response_text)
            return ideas
        except Exception as e:
            logger.error(f"Error generating ideas: {e}")
            return [
                {"id": "1", "title": f"Mẹo về {topic}", "description": "Cách làm đơn giản hiệu quả", "style": "mẹo vặt"},
                {"id": "2", "title": f"Sự thật về {topic}", "description": "Điều bạn chưa biết", "style": "kiến thức"}
            ]

    async def generate_full_script(self, idea_title: str, character_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate full script, scenes, and visual prompts for a selected idea"""
        logger.info(f"Generating full script for: {idea_title}")
        
        char_role = character_config.get("role", "Bà và cháu gái")
        char_addressing = character_config.get("addressing", "Bà - Cháu")
        
        prompt = f"""Bạn là một biên kịch chuyên nghiệp cho các kênh TikTok triệu sub. Hãy viết kịch bản chi tiết cho video: "{idea_title}"
Nhân vật: {char_role}
Cách xưng hô: {char_addressing}

Yêu cầu kịch bản PHẢI ĐẠT các tiêu chuẩn sau:
- Hook (0-3s): Cảnh đầu tiên phải cực kỳ gây tò mò hoặc hình ảnh gây sốc.
- Pacing: Chuyển cảnh nhanh, đối thoại ngắn gọn, súc tích, không lê thê.
- Emotion: Có yếu tố cảm xúc (ngạc nhiên, cười, lo lắng).
- CTA: Cảnh cuối có lời kêu gọi hành động ngầm hoặc bất ngờ.

Kịch bản chia làm 5 phân cảnh (Scene). 
Mỗi phân cảnh bao gồm:
1. Dialogue: Lời thoại tự nhiên, đời thường, có cá tính (Tiếng Việt).
2. Background: Mô tả nơi diễn ra (Tiếng Việt).
3. Visual: Mô tả chi tiết hành động, biểu cảm khuôn mặt (Tiếng Anh - cực kỳ chi tiết để AI vẽ ảnh).
4. Prompt Image-to-Video: Câu lệnh Tiếng Anh chuyên sâu (ví dụ: "Cinematic, realistic 3D, extreme close-up, dynamic motion, volumetric lighting...").

Ngoài ra cần:
- Title: Tiêu đề cuối cùng (Tiếng Việt).
- Thumbnail Prompt: Prompt Tiếng Anh để tạo ảnh bìa cực kỳ bắt mắt.

Trả về JSON format:
{{
  "title": "...",
  "thumbnail_prompt": "...",
  "scenes": [
    {{
      "scene_number": 1,
      "dialogue": "...",
      "background": "...",
      "visual_description": "...",
      "video_prompt": "..."
    }},
    ...
  ]
}}
Không giải thích gì thêm."""

        story_gen = await get_story_generator(self.ai_provider)
        try:
            response_text = await story_gen.generate_story(prompt, max_length=2000)
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            return result
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            raise

    async def generate_scene_image(self, visual_description: str, char_role: str) -> Optional[str]:
        """Generate high-quality image for a specific scene with consistent character"""
        logger.info(f"Generating scene image for: {char_role}")
        
        # Determine if we have a base prompt for this role
        # Simple heuristic: matches role name or part of it
        base_character_prompt = ""
        if "bà" in char_role.lower() or "cháu" in char_role.lower():
            base_character_prompt = get_character_base_prompt("grandparent_and_child") or ""
        elif "doanh nhân" in char_role.lower():
            base_character_prompt = get_character_base_prompt("entrepreneur") or ""
        elif "đầu bếp" in char_role.lower():
            base_character_prompt = get_character_base_prompt("chef") or ""
            
        # Advanced style modifiers for "WOW" effect
        premium_modifiers = (
            "masterpiece, highly detailed, 8k resolution, cinematic lighting, "
            "volumetric perspective, octane render, ray tracing, unreal engine 5 style, "
            "vibrant colors, sharp focus, professional photography"
        )
        
        full_prompt = (
            f"{base_character_prompt}. Environment: {visual_description}. "
            f"Style: {premium_modifiers}."
        )
        
        if not base_character_prompt:
            full_prompt = (
                f"{char_role} in a professional studio setting. Action: {visual_description}. "
                f"Aesthetic: {premium_modifiers}."
            )
        
        try:
            image_gen = await get_image_generator()
            image_url = await image_gen.generate_image(full_prompt)
            return image_url
        except Exception as e:
            logger.error(f"Error generating scene image: {e}")
            return None

    async def generate_scene_audio(self, text: str, voice: str = None) -> Optional[str]:
        """Generate TTS audio for scene dialogue"""
        logger.info(f"Generating scene audio with voice: {voice}")
        
        try:
            tts_provider = await get_tts_provider()
            audio_path, _ = await tts_provider.synthesize(text, voice=voice)
            
            # For simplicity in this demo, we'll return the absolute path as a "URL" 
            # In production, this would be served via a static assets route
            # or uploaded to S3
            return str(audio_path)
        except Exception as e:
            logger.error(f"Error generating scene audio: {e}")
            return None

    async def export_project_zip(self, project_data: Dict[str, Any]) -> str:
        """Package all project assets (images, scripts, audio) into a ZIP file"""
        project_id = uuid.uuid4().hex[:8]
        export_dir = Path(settings.TEMP_DIR) / f"export_{project_id}"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        zip_path = Path(settings.TEMP_DIR) / f"studio_project_{project_id}.zip"
        
        try:
            # 1. Save Script
            script_path = export_dir / "script.json"
            with open(script_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            
            # 2. Download/Copy Images and Audio
            async with httpx.AsyncClient() as client:
                for idx, scene in enumerate(project_data.get("scenes", [])):
                    # Image
                    img_url = scene.get("image_url")
                    if img_url:
                        if img_url.startswith("http"):
                            try:
                                resp = await client.get(img_url)
                                with open(export_dir / f"scene_{idx+1}_image.png", "wb") as f:
                                    f.write(resp.content)
                            except: pass
                        elif Path(img_url).exists():
                            shutil.copy(img_url, export_dir / f"scene_{idx+1}_image.png")
                    
                    # Audio
                    audio_url = scene.get("audio_url")
                    if audio_url:
                        if audio_url.startswith("http"):
                            try:
                                resp = await client.get(audio_url)
                                with open(export_dir / f"scene_{idx+1}_audio.mp3", "wb") as f:
                                    f.write(resp.content)
                            except: pass
                        elif Path(audio_url).exists():
                            shutil.copy(audio_url, export_dir / f"scene_{idx+1}_audio.mp3")

            # 3. Create ZIP
            with zipfile.ZipFile(zip_path, 'w') as zf:
                for file_path in export_dir.glob("*"):
                    zf.write(file_path, file_path.name)
            
            # Cleanup export dir
            shutil.rmtree(export_dir)
            
            return str(zip_path)
        except Exception as e:
            logger.error(f"Error exporting ZIP: {e}")
            raise

studio_service = StudioService()
