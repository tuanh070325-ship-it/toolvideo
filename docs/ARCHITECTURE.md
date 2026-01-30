# 🏗️ Video Processing Tool - Architecture Documentation

## Overview

Hệ thống xử lý video tự động với kiến trúc modular, hỗ trợ:
- Auto download video từ nhiều nền tảng
- Auto transcription (speech-to-text)
- Auto subtitle generation
- Auto voice replacement (TTS)
- Auto video editing và rendering
- Auto reupload

## 📦 Module Structure

```
video-tool/
├── backend/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── api/               # REST API Endpoints
│   │   │   ├── endpoints.py   # Main video processing endpoints
│   │   │   ├── studio_endpoints.py  # Studio/content creation
│   │   │   └── debug_endpoints.py   # Debug & logging endpoints
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # Environment settings
│   │   │   ├── logger.py      # Logging setup
│   │   │   └── quotas.py      # API quota management
│   │   ├── services/          # Business logic services
│   │   │   ├── external_apis/ # External API integrations
│   │   │   │   ├── base.py    # Base client with retry logic
│   │   │   │   ├── shotstack.py   # Video rendering
│   │   │   │   └── pexels.py      # Stock media
│   │   │   ├── ai/            # AI services
│   │   │   │   ├── tts_provider.py        # Text-to-speech
│   │   │   │   ├── transcription_service.py   # Speech-to-text
│   │   │   │   ├── story_generator.py     # AI story generation
│   │   │   │   └── eoa_chatbot.py         # EOA chatbot
│   │   │   ├── pipeline.py    # Video processing pipeline
│   │   │   ├── video_editor.py    # Video editing
│   │   │   ├── video_downloader.py    # Video download
│   │   │   ├── audio_processor.py     # Audio processing
│   │   │   └── text_overlay_engine.py # Text/subtitle overlay
│   │   ├── models.py          # Database models
│   │   ├── schemas.py         # Pydantic schemas
│   │   └── database.py        # Database connection
│   └── tests/                 # Backend tests
│
├── frontend/                  # Next.js Frontend
│   └── src/
│       ├── app/               # Next.js App Router
│       ├── components/        # React components
│       │   ├── ui/           # Base UI components
│       │   │   └── DebugLogPanel.tsx  # Debug logs UI
│       │   └── features/     # Feature components
│       └── lib/               # Utilities
│           └── api-client.ts  # API client
│
├── packages/                  # Shared packages (TypeScript)
│   ├── core/                  # Core library
│   ├── editor/                # Video editor module
│   └── api/                   # API server
│
└── docs/                      # Documentation
    ├── API_EVALUATION.md      # API evaluation report
    └── ARCHITECTURE.md        # This file
```

## 🔄 Video Processing Pipeline

### Pipeline Stages

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   UPLOAD    │────▶│   DOWNLOAD   │────▶│  TRANSCRIBE │
│  (Input URL)│     │ (From source)│     │(Speech→Text)│
└─────────────┘     └──────────────┘     └─────────────┘
                                               │
       ┌───────────────────────────────────────┘
       ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   ANALYZE   │────▶│ GENERATE_TTS │────▶│    EDIT     │
│(AI analysis)│     │ (Text→Voice) │     │(Video edit) │
└─────────────┘     └──────────────┘     └─────────────┘
                                               │
       ┌───────────────────────────────────────┘
       ▼
┌─────────────┐     ┌──────────────┐
│   RENDER    │────▶│    EXPORT    │
│(Final video)│     │ (Output file)│
└─────────────┘     └──────────────┘
```

### Stage Details

| Stage | Chức năng | Tools | Fallback |
|-------|-----------|-------|----------|
| UPLOAD | Nhận URL video | FastAPI | - |
| DOWNLOAD | Tải video từ nguồn | yt-dlp, httpx | TikWM API |
| TRANSCRIBE | Chuyển đổi audio→text | Whisper, Deepgram | Google STT |
| ANALYZE | Phân tích nội dung AI | GPT-4, Gemini | Mock |
| GENERATE_TTS | Tạo voice AI | Edge TTS, ElevenLabs | gTTS |
| EDIT | Chỉnh sửa video | FFmpeg | - |
| RENDER | Render video cuối | FFmpeg, Shotstack | - |
| EXPORT | Xuất file + metadata | Local storage | - |

## 🔌 External API Integration

### API Client Architecture

```python
class BaseAPIClient:
    """Base class với retry logic, error handling"""
    
    - Exponential backoff retry
    - Error categorization (401, 429, 500, etc.)
    - Request/response logging
    - Rate limit handling
    - Timeout management
```

### Error Categories

| HTTP Code | Category | Action |
|-----------|----------|--------|
| 401 | AUTH_ERROR | Check API key |
| 403 | FORBIDDEN | No retry |
| 429 | RATE_LIMITED | Backoff + retry |
| 500 | SERVER_ERROR | Retry with backoff |
| 502 | BAD_GATEWAY | Retry |
| 503 | UNAVAILABLE | Fallback to backup |

### Retry Configuration

```python
RetryConfig(
    max_retries=3,
    base_delay=1.0,  # seconds
    max_delay=60.0,  # seconds
    exponential_base=2.0,
    jitter=True,  # Prevent thundering herd
)
```

## 📊 Logging & Debug System

### Log Levels

| Level | Use Case | Example |
|-------|----------|---------|
| `debug` | Development details | "FFmpeg command: ..." |
| `info` | Normal operations | "Stage download started" |
| `success` | Completed actions | "Video rendered successfully" |
| `warning` | Non-critical issues | "Retry attempt 2/3" |
| `error` | Failures | "API request failed: 500" |

### Log Structure

```json
{
  "id": "abc123",
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "stage": "download",
  "message": "Downloading video from YouTube",
  "details": {
    "job_id": "xyz789",
    "url": "https://youtube.com/watch?v=..."
  },
  "duration": 5234
}
```

### Debug UI Features

- ✅ Real-time log streaming (SSE)
- ✅ Pipeline progress visualization
- ✅ Stage-by-stage timing
- ✅ Error highlighting
- ✅ Log filtering by level/stage
- ✅ Export logs (JSON/text)
- ✅ Debug mode toggle

## ⚙️ Configuration

### Environment Variables

```env
# Core
DEBUG=true
APP_ENV=development

# AI Providers
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
GROQ_API_KEY=...  # Free alternative

# TTS
TTS_PROVIDER=edge  # edge (free), elevenlabs, openai
EDGE_TTS_VOICE=vi-VN-HoaiMyNeural

# External APIs
SHOTSTACK_API_KEY=...  # Video rendering
PEXELS_API_KEY=...     # Stock media

# Speech-to-Text
DEEPGRAM_API_KEY=...

# Database
DATABASE_URL=mysql+pymysql://...
REDIS_URL=redis://localhost:6379/0
```

## 🚀 Processing Flows

### 1. Reup Video Flow

```
Input URL → Download → Transcribe → Generate Story → TTS → Edit → Export
```

### 2. Story Video Flow

```
Input Topic → Generate Story → TTS → Find Background → Edit → Export
```

### 3. Highlight Extraction Flow

```
Input URL → Download → Analyze → Extract Highlights → Edit → Export
```

## 🔒 Error Handling

### Error Recovery Strategy

1. **Retry** - Transient errors (timeout, 5xx)
2. **Fallback** - Use backup API
3. **Skip** - Non-critical stages
4. **Fail** - Critical errors

### Error Mapping

```python
API_ERROR_MAPPING = {
    401: "AUTH_ERROR",      # Re-authenticate
    403: "FORBIDDEN",       # Check permissions
    429: "RATE_LIMITED",    # Wait and retry
    500: "SERVER_ERROR",    # Retry with backoff
    502: "BAD_GATEWAY",     # Retry
    503: "UNAVAILABLE",     # Use fallback
}
```

## 📈 Performance Optimization

### Queue System

- Redis-based job queue
- Priority queuing
- Concurrent job limits
- Dead letter queue for failures

### Caching

- Video metadata caching
- TTS audio caching
- API response caching

### Resource Management

- Temp file cleanup
- Memory monitoring
- Disk space checks
- FFmpeg process limits

## 🧪 Testing Strategy

### Unit Tests
- Service functions
- API clients
- Utility functions

### Integration Tests
- Pipeline stages
- External API mocking
- Database operations

### E2E Tests
- Full video processing flow
- UI interaction tests

## 📚 References

- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Shotstack API](https://shotstack.io/docs/api/)
- [Pexels API](https://www.pexels.com/api/documentation/)
