# Video Tool - Complete Video Processing System

A production-ready, modular video processing tool that can download, edit, and re-upload videos across multiple social media platforms.

## 🚀 Features

### Core Capabilities

- **Multi-Platform Downloads**: YouTube, TikTok, Facebook, Instagram, Twitter
- **Advanced Video Editing**: Trim, resize, merge, watermark, audio processing
- **Platform Re-uploads**: Upload edited videos back to social platforms
- **Modular Architecture**: Extensible plugin system for new platforms
- **Production Ready**: Docker, monitoring, logging, job queues

### Supported Platforms

- **YouTube**: Download and upload with full metadata support
- **TikTok**: Short-form video processing and optimization
- **Facebook**: Video posts and stories
- **Instagram**: Reels and posts
- **Twitter**: Video tweets

### Editing Operations

- **Trimming**: Cut videos by time ranges
- **Resizing**: Convert aspect ratios (9:16, 16:9, 1:1, etc.)
- **Watermarks**: Add text or image watermarks
- **Audio Processing**: Volume adjustment, normalization, replacement
- **Merging**: Combine multiple videos
- **Highlight Extraction**: Auto-generate clips from long videos

## 📁 Architecture

```
video-tool/
├── packages/
│   ├── core/              # Core library and types
│   ├── downloader/        # Video downloader module
│   ├── editor/           # Video editor module
│   ├── uploader/         # Video uploader module
│   ├── api/              # REST API server
│   ├── cli/              # Command-line interface
│   ├── web/              # Web UI (Next.js)
│   └── sdk/              # Node.js SDK
├── infrastructure/
│   ├── docker/           # Docker configuration
│   ├── k8s/              # Kubernetes manifests
│   └── monitoring/       # Prometheus/Grafana
├── plugins/              # External plugins
├── tests/               # Test suites
└── docs/                # Documentation
```

## 🛠️ Installation

### Prerequisites

- Node.js 20+
- FFmpeg
- yt-dlp
- Docker (optional)

### Quick Start

1. **Clone and Setup**

```bash
git clone <repository-url>
cd video-tool
npm run setup
```

2. **Environment Configuration**

```bash
cp config/development.yml .env
# Edit .env with your credentials
```

3. **Start Development**

```bash
npm run dev
```

4. **Start API Server**

```bash
npm run start:api
```

### Docker Deployment

```bash
# Build and run with Docker Compose
npm run docker:build
npm run docker:run

# Or manual Docker
docker build -f infrastructure/docker/Dockerfile -t video-tool .
docker run -p 3000:3000 video-tool
```

## 📖 Usage

### REST API

#### Download a Video

```bash
curl -X POST http://localhost:3000/api/download \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://youtube.com/watch?v=example",
    "options": {
      "quality": "1080p",
      "format": "mp4",
      "subtitles": true
    }
  }'
```

#### Edit a Video

```bash
curl -X POST http://localhost:3000/api/edit \
  -H "Content-Type: application/json" \
  -d '{
    "inputPath": "/app/data/video.mp4",
    "options": {
      "trim": { "start": 10, "end": 30 },
      "resize": { "width": 1080, "height": 1920 },
      "watermark": {
        "text": "My Watermark",
        "position": "bottom-right",
        "opacity": 0.8
      }
    }
  }'
```

#### Upload a Video

```bash
curl -X POST http://localhost:3000/api/upload \
  -H "Content-Type: application/json" \
  -d '{
    "videoPath": "/app/data/edited_video.mp4",
    "platform": "youtube",
    "options": {
      "title": "My Edited Video",
      "description": "Video description",
      "tags": ["video", "editing"],
      "privacy": "public"
    }
  }'
```

### CLI Usage

```bash
# Download a video
video-tool download https://youtube.com/watch?v=example --quality 1080p

# Edit a video
video-tool edit input.mp4 --trim 10,30 --resize 1080x1920 --watermark "My Text"

# Upload a video
video-tool upload edited.mp4 --platform youtube --title "My Video"
```

### Node.js SDK

```javascript
import { VideoToolClient } from "@video-tool/sdk";

const client = new VideoToolClient({
  apiUrl: "http://localhost:3000",
  apiKey: "your-api-key",
});

// Download
const video = await client.download("https://youtube.com/watch?v=example");

// Edit
const edited = await client.edit(video.path, {
  trim: { start: 10, end: 30 },
  resize: { width: 1080, height: 1920 },
});

// Upload
const result = await client.upload(edited.path, "youtube", {
  title: "My Video",
  description: "Video description",
});
```

## ⚙️ Configuration

### Environment Variables

```yaml
# Storage
STORAGE_TYPE: local # local | s3
STORAGE_LOCAL_PATH: ./data # Local storage path
AWS_S3_BUCKET: my-bucket # S3 bucket name
AWS_REGION: us-east-1 # AWS region

# Queue
QUEUE_TYPE: memory # memory | redis
REDIS_HOST: localhost # Redis host
REDIS_PORT: 6379 # Redis port

# Logging
LOG_LEVEL: info # debug | info | warn | error
LOG_FORMAT: pretty # json | pretty

# Concurrency
CONCURRENCY_DOWNLOADS: 3 # Max concurrent downloads
CONCURRENCY_EDITS: 2 # Max concurrent edits
CONCURRENCY_UPLOADS: 2 # Max concurrent uploads

# Platform Credentials
YOUTUBE_API_KEY: your-key # YouTube Data API key
TIKTTOKEN: your-token # TikTok API token
FACEBOOK_ACCESS_TOKEN: token # Facebook access token
```

### Platform Setup

#### YouTube

1. Create a Google Cloud Project
2. Enable YouTube Data API v3
3. Create API credentials
4. Set `YOUTUBE_API_KEY` environment variable

#### TikTok

1. Apply for TikTok Developer access
2. Create an app and get API key
3. Set `TIKTOK_API_KEY` environment variable

#### Facebook

1. Create a Facebook Developer account
2. Create a Page Access Token
3. Set `FACEBOOK_ACCESS_TOKEN` environment variable

## 🔧 Plugin Development

Create custom plugins for new platforms:

```typescript
import { DownloaderPlugin, VideoFile, Platform } from "@video-tool/core";

export class CustomPlatformDownloader implements DownloaderPlugin {
  name = "custom-downloader";
  platform = Platform.CUSTOM;

  canHandle(url: string): boolean {
    return url.includes("custom-platform.com");
  }

  async download(url: string, options?: DownloadOptions): Promise<VideoFile> {
    // Implement download logic
  }

  async getMetadata(url: string): Promise<VideoMetadata> {
    // Implement metadata extraction
  }
}
```

## 📊 Monitoring

### Health Checks

- API: `GET /api/health`
- Individual services health status
- Job queue status

### Metrics

- Download success/failure rates
- Processing times
- Storage usage
- API request counts

### Logging

Structured logging with:

- Request tracing
- Error context
- Performance metrics
- Job status updates

## 🧪 Testing

```bash
# Run all tests
npm test

# Run specific package tests
npm run test --workspace=@video-tool/core

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e
```

## 🚀 Deployment

### Production Docker

```bash
# Build production image
docker build -f infrastructure/docker/Dockerfile -t video-tool:latest .

# Run with environment file
docker run -d \
  --name video-tool \
  -p 3000:3000 \
  --env-file .env \
  -v video_data:/app/data \
  video-tool:latest
```

### Kubernetes

```bash
# Apply manifests
kubectl apply -f infrastructure/k8s/

# Check status
kubectl get pods -n video-tool
```

### Scaling

- **Horizontal**: Increase container replicas
- **Vertical**: Increase resource limits
- **Queue Scaling**: Add more worker processes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Workflow

```bash
# Install dependencies
npm install

# Start development mode
npm run dev

# Run type checking
npm run typecheck

# Run linting
npm run lint

# Build all packages
npm run build
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [docs/](./docs/)
- **API Reference**: [docs/api/](./docs/api/)
- **Examples**: [docs/examples/](./docs/examples/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/video-tool/issues)

## 🗺️ Roadmap

### v1.1

- [ ] Web UI dashboard
- [ ] Batch processing
- [ ] Advanced AI features
- [ ] Mobile app

### v1.2

- [ ] Cloud storage integration
- [ ] Advanced analytics
- [ ] Team collaboration
- [ ] API rate limiting

### v2.0

- [ ] Real-time processing
- [ ] Live streaming support
- [ ] Advanced templates
- [ ] Enterprise features

---

**Built with ❤️ for the video processing community**
