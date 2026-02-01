
import sys
import os
import json
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from pathlib import Path
from fastapi import APIRouter, WebSocket, Request, UploadFile, File, Form, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.core.logger import logger
from app.core.config import settings

# Add ComfyUI engine to path
COMFY_PATH = Path("backend/comfyui_engine").absolute()
sys.path.append(str(COMFY_PATH))

# Import ComfyUI modules
# We wrap this in try-except to avoid crashing if imports fail during dev
try:
    import nodes
    import execution
    import folder_paths
    import server
except ImportError as e:
    logger.error(f"Failed to import ComfyUI modules: {e}")
    # We might need to handle this gracefully or ensure dependencies are installed
    pass

router = APIRouter()

# Global state for ComfyUI integration
class ComfyMyApp:
    def __init__(self):
        self.prompt_queue = None
        self.client_id = "default_client"
        self.sockets: Dict[str, WebSocket] = {}
        self.last_node_id = None
    
    def init_engine(self):
        if not 'nodes' in sys.modules:
            logger.error("ComfyUI modules not loaded")
            return
        
        # Initialize ComfyUI paths
        # folder_paths.set_output_directory(settings.PROCESSED_DIR)
        # folder_paths.set_input_directory(settings.DOWNLOADS_DIR)
        
        # Initialize execution queue
        # process_queue uses server object to send messages
        self.prompt_queue = execution.PromptQueue(self)
        
        # Load nodes
        nodes.init_extra_nodes()

    async def send_json(self, event: str, data: Dict[str, Any], sid: Optional[str] = None):
        """Send JSON message to websockets"""
        message = {"type": event, "data": data}
        if sid and sid in self.sockets:
            try:
                await self.sockets[sid].send_json(message)
            except Exception as e:
                logger.error(f"WS Error: {e}")
                del self.sockets[sid]
        else:
            # Broadcast
            for ws_id, ws in list(self.sockets.items()):
                try:
                    await ws.send_json(message)
                except Exception:
                    del self.sockets[ws_id]
    
    def send_sync(self, event, data, sid=None):
        """Synchronous wrapper for execution thread"""
        asyncio.run_coroutine_threadsafe(self.send_json(event, data, sid), asyncio.get_event_loop())

    def get_queue_info(self):
        return self.prompt_queue.get_current_queue_volatile()

comfy_app = ComfyMyApp()

# Patch the server.PromptServer instance so nodes can communicate back
# This is critical for nodes that send progress/status updates
try:
    if 'server' in sys.modules:
        server.PromptServer.instance = comfy_app
except Exception:
    pass

@router.on_event("startup")
async def startup_event():
    logger.info("Initializing ComfyUI Engine...")
    try:
        if 'nodes' in sys.modules:
             # Ensure folder paths are setup (using ComfyUI defaults or overrides)
            cwd = os.getcwd()
            os.chdir(COMFY_PATH) # Comfy expects to be in its root for some loaders
            comfy_app.init_engine()
            os.chdir(cwd) # Restore
            logger.info("ComfyUI Engine Initialized")
    except Exception as e:
        logger.error(f"ComfyUI Init Failed: {e}")

# --- API Endpoints matching ComfyUI ---

@router.get("/object_info")
async def get_object_info():
    """Get all node definitions"""
    out = {}
    for x in nodes.NODE_CLASS_MAPPINGS:
        try:
             # Logic from server.py node_info
            obj_class = nodes.NODE_CLASS_MAPPINGS[x]
            info = {}
            info['input'] = obj_class.INPUT_TYPES()
            info['output'] = obj_class.RETURN_TYPES
            info['output_name'] = getattr(obj_class, 'RETURN_NAMES', info['output'])
            info['name'] = x
            info['display_name'] = nodes.NODE_DISPLAY_NAME_MAPPINGS.get(x, x)
            info['description'] = getattr(obj_class, 'DESCRIPTION', '')
            info['category'] = getattr(obj_class, 'CATEGORY', 'sd')
            info['output_node'] = getattr(obj_class, 'OUTPUT_NODE', False)
            out[x] = info
        except Exception as e:
            logger.error(f"Error getting info for {x}: {e}")
            
    return out

@router.get("/embeddings")
async def get_embeddings():
    return []

@router.get("/extensions")
async def get_extensions():
    return [] # TODO: Scan web/extensions

@router.post("/prompt")
async def post_prompt(request: Request):
    data = await request.json()
    # Queue prompt
    # data format: {"prompt": {...}, "client_id": ...}
    
    json_prompt = data.get("prompt")
    client_id = data.get("client_id")
    
    if not json_prompt:
        return Response(status_code=400)

    # Validate and add to queue
    # logic from server.py
    
    # We use comfy_app.prompt_queue
    # But queue expects (number, prompt_id, prompt, extra_data, outputs_to_execute)
    
    prompt_id = str(uuid.uuid4())
    valid = execution.validate_prompt(json_prompt)
    
    if not valid[0]:
        return JSONResponse({"error": valid[1], "node_errors": valid[2]}, status_code=400)
    
    outputs_to_execute = valid[3]
    comfy_app.prompt_queue.put((0, prompt_id, json_prompt, {"client_id": client_id}, outputs_to_execute))
    
    return {"prompt_id": prompt_id, "number": 1, "node_errors": {}}

@router.get("/queue")
async def get_queue():
    running, pending = comfy_app.prompt_queue.get_current_queue_volatile()
    return {"queue_running": running, "queue_pending": pending}

@router.get("/history")
async def get_history():
    return comfy_app.prompt_queue.get_history()

@router.get("/system_stats")
async def get_system_stats():
    return {
        "system": {
            "os": sys.platform,
            "python_version": sys.version,
            "comfyui_version": "custom_integration"
        },
        "devices": []
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, clientId: str = ""):
    await websocket.accept()
    if not clientId:
        clientId = str(uuid.uuid4())
    
    comfy_app.sockets[clientId] = websocket
    
    try:
        # Send status
        status = comfy_app.get_queue_info()
        await websocket.send_json({"type": "status", "data": {"status": status, "sid": clientId}})
        
        while True:
            data = await websocket.receive_text()
            # keep alive
    except Exception:
        if clientId in comfy_app.sockets:
            del comfy_app.sockets[clientId]

