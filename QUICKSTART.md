# Quick Start Guide

## 🚀 Getting Started

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install 120+ packages including:
- PyTorch and AI libraries
- LTX-Video dependencies
- Monitoring and memory tools
- All existing video processing tools

**Note**: Installation may take 15-30 minutes depending on your internet speed.

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# Minimum required:
# - OPENAI_API_KEY or GROQ_API_KEY (for AI features)
# - LTX_DEVICE=cuda (or cpu if no GPU)
```

### 3. Test Integration

```bash
cd backend
python test_integration.py
```

This will verify all services are properly configured.

### 4. Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 5. Access API

- **API Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/health
- **Generation Status**: http://localhost:8000/api/generation/status

## 📝 Quick API Examples

### Generate Video from Text

```bash
curl -X POST http://localhost:8000/api/generation/text-to-video \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat playing with a ball in a sunny garden",
    "num_frames": 121,
    "height": 704,
    "width": 1216
  }'
```

### Create Workflow

```bash
curl -X POST http://localhost:8000/api/workflows/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Workflow",
    "description": "Test workflow",
    "nodes": [
      {"id": "1", "type": "VideoDownload"},
      {"id": "2", "type": "VideoExport"}
    ],
    "connections": [
      {
        "source_node": "1",
        "source_output": "video_path",
        "target_node": "2",
        "target_input": "video_path"
      }
    ]
  }'
```

### List Workflows

```bash
curl http://localhost:8000/api/workflows/list
```

## 🎯 Next Steps

1. **Download Models** (optional, for AI generation):
   ```bash
   # LTX-Video model (~26GB)
   huggingface-cli download Lightricks/LTX-Video \
     ltxv-13b-0.9.8-distilled.safetensors \
     --local-dir models/ltx-video
   ```

2. **Configure Monitoring** (optional):
   - Sign up for Opik: https://www.comet.com/opik
   - Add `OPIK_API_KEY` to `.env`

3. **Explore Features**:
   - Try AI video generation
   - Create custom workflows
   - Test video processing

4. **Read Full Documentation**:
   - [README.md](README.md) - Complete feature guide
   - [INSTALLATION.md](INSTALLATION.md) - Detailed setup
   - API Docs: http://localhost:8000/api/docs

## ⚡ Performance Tips

- **GPU Required**: AI generation needs NVIDIA GPU with 8GB+ VRAM
- **CPU Mode**: Set `LTX_DEVICE=cpu` (much slower)
- **Memory**: 16GB RAM minimum, 32GB recommended
- **Storage**: Keep 50GB+ free for models and outputs

## 🆘 Troubleshooting

**Import Errors**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**CUDA Errors**:
```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Port in Use**:
```bash
# Use different port
uvicorn app.main:app --port 8001
```

## 📚 Resources

- **LTX-Video**: https://github.com/Lightricks/LTX-Video
- **ComfyUI**: https://github.com/Comfy-Org/ComfyUI
- **Opik**: https://www.comet.com/docs/opik/
- **API Docs**: http://localhost:8000/api/docs

---

**Ready to create amazing videos with AI! 🎬✨**
