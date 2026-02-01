"""API routes for ComfyUI-style workflow management"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import json
from pathlib import Path
from datetime import datetime

from app.core.logger import logger

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Workflow storage directory
WORKFLOWS_DIR = Path("backend/data/workflows")
WORKFLOWS_DIR.mkdir(parents=True, exist_ok=True)


class WorkflowNode(BaseModel):
    """A single node in a workflow"""
    id: str
    type: str  # e.g., "VideoDownload", "VideoProcess", "LTXGeneration"
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    position: Dict[str, float] = Field(default_factory=dict)  # x, y coordinates


class WorkflowConnection(BaseModel):
    """Connection between two nodes"""
    source_node: str
    source_output: str
    target_node: str
    target_input: str


class Workflow(BaseModel):
    """Complete workflow definition"""
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    nodes: List[WorkflowNode]
    connections: List[WorkflowConnection]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class WorkflowExecutionRequest(BaseModel):
    """Request to execute a workflow"""
    workflow_id: str
    inputs: Dict[str, Any] = Field(default_factory=dict)


class WorkflowExecutionResponse(BaseModel):
    """Response from workflow execution"""
    success: bool
    execution_id: str
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@router.post("/create", response_model=Workflow)
async def create_workflow(workflow: Workflow):
    """Create a new workflow
    
    Workflows are ComfyUI-style node graphs that define
    a sequence of video processing operations.
    """
    try:
        # Generate ID if not provided
        if not workflow.id:
            workflow.id = f"workflow_{int(datetime.now().timestamp())}"
        
        # Set timestamps
        workflow.created_at = datetime.now().isoformat()
        workflow.updated_at = workflow.created_at
        
        # Save to file
        workflow_path = WORKFLOWS_DIR / f"{workflow.id}.json"
        with open(workflow_path, "w") as f:
            json.dump(workflow.dict(), f, indent=2)
        
        logger.info(f"Created workflow: {workflow.id} - {workflow.name}")
        
        return workflow
        
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_workflows():
    """List all saved workflows"""
    try:
        workflows = []
        
        for workflow_file in WORKFLOWS_DIR.glob("*.json"):
            with open(workflow_file, "r") as f:
                workflow_data = json.load(f)
                workflows.append({
                    "id": workflow_data.get("id"),
                    "name": workflow_data.get("name"),
                    "description": workflow_data.get("description"),
                    "created_at": workflow_data.get("created_at"),
                    "node_count": len(workflow_data.get("nodes", [])),
                })
        
        return {"workflows": workflows}
        
    except Exception as e:
        logger.error(f"Failed to list workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_workflow_templates():
    """List predefined workflow templates"""
    templates = [
        # 1. Basic Video Processing (Comfy-like pipeline)
        {
            "id": "full_pipeline_v1",
            "name": "Complete Video Pipeline (Download -> Trim -> Resize)",
            "description": "Standard editing workflow: Download, Trim, and Resize for TikTok/Shorts",
            "nodes": [
                {
                    "id": "download_1",
                    "type": "VideoDownload",
                    "inputs": {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "platform": "youtube"},
                    "position": {"x": 50, "y": 100}
                },
                {
                    "id": "trim_1",
                    "type": "VideoTrim",
                    "inputs": {"start_time": 0, "end_time": 30},
                    "position": {"x": 350, "y": 100}
                },
                {
                    "id": "resize_1",
                    "type": "VideoResize",
                    "inputs": {"width": 1080, "height": 1920},
                    "position": {"x": 650, "y": 100}
                },
                {
                    "id": "export_1",
                    "type": "VideoExport",
                    "inputs": {"format": "mp4"},
                    "position": {"x": 950, "y": 100}
                }
            ],
            "connections": [
                {"source_node": "download_1", "source_output": "video_path", "target_node": "trim_1", "target_input": "video_path"},
                {"source_node": "trim_1", "source_output": "output_path", "target_node": "resize_1", "target_input": "video_path"},
                {"source_node": "resize_1", "source_output": "output_path", "target_node": "export_1", "target_input": "video_path"}
            ]
        },

        # 2. AI Video Generation (Text-to-Video)
        {
            "id": "txt2vid_ltx",
            "name": "Text-to-Video (LTX-Video Mode)",
            "description": "Generate high-quality video from text prompt using LTX-Video model",
            "nodes": [
                {
                    "id": "prompt_enhance",
                    "type": "VideoProcess", # Placeholder for prompt enhancement logic if needed
                    "inputs": {"operations": {"enhance_prompt": True}},
                    "position": {"x": 50, "y": 100}
                },
                {
                    "id": "ltx_gen",
                    "type": "LTXGeneration",
                    "inputs": {
                        "prompt": "Cinematic drone shot of a futuristic cyberpunk city, neon lights, rain, high detail, 8k",
                        "negative_prompt": "low quality, blurry, distorted",
                        "num_frames": 121,
                        "seed": 42
                    },
                    "position": {"x": 350, "y": 100}
                },
                {
                    "id": "export_vid",
                    "type": "VideoExport",
                    "inputs": {"format": "mp4"},
                    "position": {"x": 700, "y": 100}
                }
            ],
            "connections": [
                {"source_node": "ltx_gen", "source_output": "video_path", "target_node": "export_vid", "target_input": "video_path"}
            ]
        },

        # 3. Image-to-Video (Animation)
        {
            "id": "img2vid_ltx",
            "name": "Image-to-Video Animation",
            "description": "Animate a static image into a video using AI",
            "nodes": [
                 # Assuming we'd have an ImageLoad node, but for now passing path directly
                {
                    "id": "img2vid",
                    "type": "ImageToVideo", 
                    "inputs": {
                        "image_path": "data/uploads/image.png",
                        "prompt": "Animate this image, camera zoom in",
                        "num_frames": 121
                    },
                    "position": {"x": 350, "y": 100}
                },
                {
                    "id": "export_vid",
                    "type": "VideoExport",
                    "inputs": {"format": "mp4"},
                    "position": {"x": 700, "y": 100}
                }
            ],
            "connections": [
                {"source_node": "img2vid", "source_output": "video_path", "target_node": "export_vid", "target_input": "video_path"}
            ]
        },

        # 4. Auto Cut (Smart Highlights)
        {
            "id": "auto_cut_highlights",
            "name": "Auto Cut Highlights (AI Analysis)",
            "description": "Automatically extract best moments from long video",
            "nodes": [
                {
                    "id": "download_src",
                    "type": "VideoDownload",
                    "inputs": {"url": "https://www.youtube.com/watch?v=some_podcast", "platform": "youtube"},
                    "position": {"x": 50, "y": 100}
                },
                {
                    "id": "auto_cut",
                    "type": "HighlightExtraction",
                    "inputs": {
                        "num_highlights": 3,
                        "duration": 60,
                        "style": "engaging"
                    },
                    "position": {"x": 350, "y": 100}
                }
            ],
            "connections": [
                {"source_node": "download_src", "source_output": "video_path", "target_node": "auto_cut", "target_input": "video_path"}
            ]
        },

        # 5. Voice Reup (TTS + Reup)
        {
            "id": "voice_reup_auto",
            "name": "Auto Voice Reup (TTS + Edit)",
            "description": "Generate AI voiceover and re-upload video with captions",
            "nodes": [
                {
                    "id": "download_src",
                    "type": "VideoDownload",
                    "inputs": {"url": "", "platform": "tiktok"},
                    "position": {"x": 50, "y": 50}
                },
                {
                    "id": "tts_gen",
                    "type": "TTSGeneration",
                    "inputs": {
                        "text": "This is a new narration for the video generated by AI.",
                        "voice": "alloy",
                        "provider": "auto"
                    },
                    "position": {"x": 50, "y": 250}
                },
                {
                    "id": "reup_proc",
                    "type": "VideoReup",
                    "inputs": {
                        "platform": "tiktok",
                        "add_captions": True
                    },
                    "position": {"x": 400, "y": 150}
                }
            ],
            "connections": [
                {"source_node": "download_src", "source_output": "video_path", "target_node": "reup_proc", "target_input": "video_path"},
                {"source_node": "tts_gen", "source_output": "audio_path", "target_node": "reup_proc", "target_input": "audio_path"}
            ]
        }
    ]
    
    return {"templates": templates}


@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str):
    """Get a specific workflow by ID"""
    try:
        workflow_path = WORKFLOWS_DIR / f"{workflow_id}.json"
        
        if not workflow_path.exists():
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        with open(workflow_path, "r") as f:
            workflow_data = json.load(f)
        
        return Workflow(**workflow_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{workflow_id}", response_model=Workflow)
async def update_workflow(workflow_id: str, workflow: Workflow):
    """Update an existing workflow"""
    try:
        workflow_path = WORKFLOWS_DIR / f"{workflow_id}.json"
        
        if not workflow_path.exists():
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Update timestamp
        workflow.id = workflow_id
        workflow.updated_at = datetime.now().isoformat()
        
        # Save
        with open(workflow_path, "w") as f:
            json.dump(workflow.dict(), f, indent=2)
        
        logger.info(f"Updated workflow: {workflow_id}")
        
        return workflow
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete a workflow"""
    try:
        workflow_path = WORKFLOWS_DIR / f"{workflow_id}.json"
        
        if not workflow_path.exists():
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        workflow_path.unlink()
        
        logger.info(f"Deleted workflow: {workflow_id}")
        
        return {"message": f"Workflow {workflow_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(request: WorkflowExecutionRequest):
    """Execute a workflow
    
    This will run all nodes in the workflow in the correct order
    based on their connections.
    """
    try:
        # Load workflow
        workflow_path = WORKFLOWS_DIR / f"{request.workflow_id}.json"
        
        if not workflow_path.exists():
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        with open(workflow_path, "r") as f:
            workflow_data = json.load(f)
        
        workflow = Workflow(**workflow_data)
        
        # Generate execution ID
        execution_id = f"exec_{int(datetime.now().timestamp())}"
        
        logger.info(f"Executing workflow: {workflow.name} (ID: {execution_id})")
        
        # Execute workflow using executor
        from app.workflows import get_workflow_executor
        executor = get_workflow_executor()
        
        result = await executor.execute_workflow(
            workflow=workflow.dict(),
            inputs=request.inputs
        )
        
        return WorkflowExecutionResponse(
            success=True,
            execution_id=result["execution_id"],
            outputs=result["outputs"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        return WorkflowExecutionResponse(
            success=False,
            execution_id="",
            error=str(e)
        )
