# Installation Guide - Video Tool

Complete installation guide for the AI-powered video processing platform.

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Quick Installation](#quick-installation)
3. [Detailed Installation](#detailed-installation)
4. [Model Downloads](#model-downloads)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Verification](#verification)

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, Ubuntu 20.04+, or macOS 12+
- **CPU**: 4+ cores
- **RAM**: 16GB
- **Storage**: 50GB free space
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for AI generation)
- **Python**: 3.10 or 3.11
- **Node.js**: 18.x or 20.x

### Recommended Requirements
- **CPU**: 8+ cores
- **RAM**: 32GB
- **GPU**: NVIDIA RTX 3090/4090 or A100 (24GB+ VRAM)
- **Storage**: 100GB+ SSD
- **Internet**: High-speed connection for model downloads

---

## Quick Installation

### Windows

```powershell
# 1. Clone repository
git clone <your-repo-url>
cd video_tool

# 2. Create Python virtual environment
cd backend
python -m venv venv
venv\Scripts\activate

# 3. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Node.js dependencies
cd ..\frontend
npm install

# 5. Set up environment
cd ..
copy .env.example .env
# Edit .env with your configuration

# 6. Initialize database
cd backend
alembic upgrade head

# 7. Start services
# Terminal 1:
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2:
cd frontend
npm run dev
```

### Linux/Mac

```bash
# 1. Clone repository
git clone <your-repo-url>
cd video_tool

# 2. Create Python virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# 3. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Install Node.js dependencies
cd ../frontend
npm install

# 5. Set up environment
cd ..
cp .env.example .env
# Edit .env with your configuration

# 6. Initialize database
cd backend
alembic upgrade head

# 7. Start services
# Terminal 1:
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2:
cd frontend
npm run dev
```

---

## Detailed Installation

### Step 1: Install System Dependencies

#### Windows

1. **Install Python 3.10/3.11**
   - Download from [python.org](https://www.python.org/downloads/)
   - Check "Add Python to PATH" during installation

2. **Install Node.js 18.x**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version` and `npm --version`

3. **Install Git**
   - Download from [git-scm.com](https://git-scm.com/)

4. **Install CUDA Toolkit** (for GPU support)
   - Download CUDA 11.8 or 12.1 from [NVIDIA](https://developer.nvidia.com/cuda-downloads)
   - Install cuDNN

5. **Install FFmpeg**
   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Add to PATH or place in `backend/` directory

#### Linux (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install Git
sudo apt install git -y

# Install FFmpeg
sudo apt install ffmpeg -y

# Install CUDA (for GPU support)
# Follow NVIDIA's official guide for your Ubuntu version
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
sudo apt update
sudo apt install cuda -y
```

#### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.10
brew install python@3.10

# Install Node.js 18
brew install node@18

# Install FFmpeg
brew install ffmpeg

# Install Git
brew install git
```

### Step 2: Clone Repository

```bash
git clone <your-repo-url>
cd video_tool
```

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# This may take 10-30 minutes depending on your internet speed
# PyTorch alone is ~2GB
```

### Step 4: Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# This may take 5-10 minutes
```

### Step 5: Database Initialization

```bash
cd ../backend

# Run migrations
alembic upgrade head

# Verify database created
ls -la  # Should see video_reup.db
```

---

## Model Downloads

### LTX-Video Models

Models are downloaded automatically on first use, but you can pre-download:

```bash
# Create models directory
mkdir -p models/ltx-video

# Download model (choose one):

# Option 1: 13B Distilled (Recommended - 26GB)
huggingface-cli download Lightricks/LTX-Video \
  ltxv-13b-0.9.8-distilled.safetensors \
  --local-dir models/ltx-video

# Option 2: 2B Distilled (Faster - 4GB)
huggingface-cli download Lightricks/LTX-Video \
  ltxv-2b-0.9.8-distilled.safetensors \
  --local-dir models/ltx-video

# Option 3: 13B Dev (Best Quality - 26GB)
huggingface-cli download Lightricks/LTX-Video \
  ltxv-13b-0.9.8-dev.safetensors \
  --local-dir models/ltx-video
```

### Text Encoder (Required)

```bash
# Download T5 encoder (will auto-download on first use)
# Or manually:
huggingface-cli download google/t5-v1_1-xxl \
  --local-dir models/t5-v1_1-xxl
```

### Disk Space Requirements

- **LTX-Video 13B**: ~26GB
- **LTX-Video 2B**: ~4GB
- **T5 Encoder**: ~10GB
- **Total**: 40-50GB for full setup

---

## Configuration

### Environment Variables

1. **Copy example file**:
```bash
cp .env.example .env
```

2. **Edit `.env` file**:

```env
# Required API Keys
OPENAI_API_KEY=sk-...  # For GPT models
GROQ_API_KEY=gsk_...   # For fast inference
OPIK_API_KEY=...       # For monitoring (optional)

# LTX-Video Configuration
LTX_MODEL_PATH=models/ltx-video/ltxv-13b-0.9.8-distilled.safetensors
LTX_DEVICE=cuda  # or 'cpu' if no GPU
LTX_PRECISION=bfloat16  # or 'float8_e4m3fn' for FP8

# Paths
UPLOAD_DIR=backend/uploads
OUTPUT_DIR=backend/data/outputs
MODELS_DIR=models
```

### GPU Configuration

**For NVIDIA GPUs:**
```env
LTX_DEVICE=cuda
LTX_PRECISION=bfloat16  # Best quality
# or
LTX_PRECISION=float8_e4m3fn  # Faster, less VRAM
```

**For CPU (slower):**
```env
LTX_DEVICE=cpu
LTX_PRECISION=bfloat16
LTX_OFFLOAD_CPU=true
```

**For Apple Silicon (M1/M2/M3):**
```env
LTX_DEVICE=mps
LTX_PRECISION=bfloat16
```

---

## Troubleshooting

### Common Issues

#### 1. CUDA Out of Memory

**Error**: `RuntimeError: CUDA out of memory`

**Solutions**:
- Use smaller model: `ltxv-2b-0.9.8-distilled.safetensors`
- Enable CPU offloading: `LTX_OFFLOAD_CPU=true`
- Reduce resolution: `LTX_HEIGHT=512`, `LTX_WIDTH=768`
- Use FP8 precision: `LTX_PRECISION=float8_e4m3fn`

#### 2. Import Errors

**Error**: `ModuleNotFoundError: No module named 'torch'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 3. FFmpeg Not Found

**Error**: `FileNotFoundError: ffmpeg not found`

**Solution**:
- **Windows**: Download FFmpeg and place `ffmpeg.exe` in `backend/` directory
- **Linux**: `sudo apt install ffmpeg`
- **Mac**: `brew install ffmpeg`

#### 4. Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Change port in command
uvicorn app.main:app --port 8001  # Backend
npm run dev -- -p 3001  # Frontend
```

#### 5. Database Migration Errors

**Error**: `alembic.util.exc.CommandError`

**Solution**:
```bash
# Reset database
rm video_reup.db
alembic upgrade head
```

---

## Verification

### 1. Check Backend

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# In another terminal, test:
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "checks": {
    "api": true,
    "database": true,
    "redis": true,
    "storage": true
  }
}
```

### 2. Check Frontend

```bash
# Start frontend
cd frontend
npm run dev
```

Open browser: http://localhost:3000

### 3. Test AI Generation

```bash
curl -X POST http://localhost:8000/api/generation/status
```

Expected response:
```json
{
  "service": "ltx-video",
  "initialized": false,
  "available": true
}
```

### 4. Test Video Download

```bash
curl -X POST http://localhost:8000/api/videos/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

---

## Next Steps

1. **Read the [README.md](README.md)** for usage examples
2. **Explore API docs**: http://localhost:8000/api/docs
3. **Try workflow templates**: http://localhost:3000/workflows
4. **Configure monitoring**: Set up Opik dashboard
5. **Customize settings**: Edit `.env` for your needs

---

## Support

If you encounter issues:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs in `backend/logs/`
3. Check GitHub Issues
4. Join our Discord community

---

**Installation complete! 🎉**

You're now ready to process and generate videos with AI!