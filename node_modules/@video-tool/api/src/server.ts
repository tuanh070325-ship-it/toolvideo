import express from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import { config, VideoFile } from "@video-tool/core";
import { VideoDownloader } from "@video-tool/downloader";
import { VideoEditor } from "@video-tool/editor";
import { VideoUploader } from "@video-tool/uploader";
import { createLogger, type Logger } from "@video-tool/core";

const app = express();
const PORT = process.env.PORT || 3000;
const logger = createLogger(config.logging.level, config.logging.format);

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: "Too many requests from this IP",
});
app.use("/api/", limiter);

// Initialize components
const downloader = new VideoDownloader();
const editor = new VideoEditor();
const uploader = new VideoUploader();

// Request logger middleware
app.use((req, res, next) => {
  const traceId = Math.random().toString(36).substr(2, 9);
  req.headers["x-trace-id"] = traceId;
  logger.child({ traceId }).info(`${req.method} ${req.path}`, {
    method: req.method,
    path: req.path,
    ip: req.ip,
    userAgent: req.headers["user-agent"],
  });
  next();
});

// Routes
app.get("/api/health", (req, res) => {
  const traceId = req.headers["x-trace-id"];
  const childLogger = logger.child({ traceId });

  childLogger.info("Health check requested", {
    method: "GET",
    path: "/api/health",
  });

  res.json({
    success: true,
    status: "ok",
    timestamp: new Date().toISOString(),
    traceId,
  });
});

app.post("/api/download", async (req, res) => {
  const traceId = req.headers["x-trace-id"];
  const childLogger = logger.child({ traceId });

  try {
    childLogger.info("Download request received", { body: req.body });

    const { url, options } = req.body;

    // Input validation
    if (!url) {
      childLogger.warn("Missing required field", { field: "url" });
      return res.status(400).json({
        success: false,
        error: "URL is required",
        traceId,
      });
    }

    if (typeof url !== "string" || !url.startsWith("http")) {
      childLogger.warn("Invalid URL format", { url });
      return res.status(400).json({
        success: false,
        error: "Invalid URL format",
        traceId,
      });
    }

    childLogger.info("Starting video download", { url, options });
    const videoFile = await downloader.download(url, options || {});

    childLogger.info("Video download completed", {
      videoPath: videoFile.path,
      size: videoFile.size,
    });

    res.json({
      success: true,
      data: videoFile,
      traceId,
    });
  } catch (error) {
    childLogger.error("Download request failed", error as Error, {
      body: req.body,
    });
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Download failed",
      traceId,
    });
  }
});

app.post("/api/edit", async (req, res) => {
  const traceId = req.headers["x-trace-id"];
  const childLogger = logger.child({ traceId });

  try {
    childLogger.info("Edit request received", { body: req.body });

    const { inputPath, options } = req.body;

    // Input validation
    if (!inputPath || !options) {
      childLogger.warn("Missing required fields", {
        inputPath,
        hasOptions: !!options,
      });
      return res.status(400).json({
        success: false,
        error: "Input path and options are required",
        traceId,
      });
    }

    // Security: validate file path to prevent directory traversal
    const sanitizedPath = inputPath
      .replace(/\.\./g, "")
      .replace(/[\/\\]/g, "_");
    if (!sanitizedPath.startsWith("data_")) {
      childLogger.warn("Invalid file path", {
        originalPath: inputPath,
        sanitizedPath,
      });
      return res.status(400).json({
        success: false,
        error: "Invalid file path",
        traceId,
      });
    }

    // Create VideoFile object from path
    const inputVideo: VideoFile = {
      path: sanitizedPath,
      name: sanitizedPath.split("_").pop() || "video.mp4",
      extension: sanitizedPath.split(".").pop() || "mp4",
      mimeType: "video/mp4",
      size: 0, // Will be determined by fs operations
    };

    childLogger.info("Starting video edit", {
      inputPath: sanitizedPath,
      operations: Object.keys(options),
    });

    const outputVideo = await editor.edit(inputVideo, options);

    childLogger.info("Video edit completed", {
      outputPath: outputVideo.path,
      operations: Object.keys(options),
    });

    res.json({
      success: true,
      data: outputVideo,
      traceId,
    });
  } catch (error) {
    childLogger.error("Edit request failed", error as Error, {
      body: req.body,
    });
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Edit failed",
      traceId,
    });
  }
});

app.post("/api/upload", async (req, res) => {
  const traceId = req.headers["x-trace-id"];
  const childLogger = logger.child({ traceId });

  try {
    childLogger.info("Upload request received", { body: req.body });

    const { videoPath, platform, options } = req.body;

    // Input validation
    if (!videoPath || !platform) {
      childLogger.warn("Missing required fields", { videoPath, platform });
      return res.status(400).json({
        success: false,
        error: "Video path and platform are required",
        traceId,
      });
    }

    // Validate platform
    const validPlatforms = [
      "youtube",
      "tiktok",
      "facebook",
      "instagram",
      "twitter",
    ];
    if (!validPlatforms.includes(platform)) {
      childLogger.warn("Invalid platform", { platform, validPlatforms });
      return res.status(400).json({
        success: false,
        error: "Invalid platform",
        traceId,
      });
    }

    // Create VideoFile object
    const videoFile: VideoFile = {
      path: videoPath,
      name: videoPath.split(/[\/\\]/).pop() || "video.mp4",
      extension: videoPath.split(".").pop() || "mp4",
      mimeType: "video/mp4",
      size: 0,
    };

    // Set credentials (in production, these would come from secure config)
    uploader.setCredentials(platform as any, {
      apiKey: process.env[`${platform.toUpperCase()}_API_KEY`] || "test-key",
    });

    childLogger.info("Starting video upload", {
      platform,
      videoPath,
      options,
    });

    const result = await uploader.upload(
      videoFile,
      platform as any,
      options || {},
    );

    childLogger.info("Video upload completed", {
      platform,
      uploadId: result.id,
      uploadUrl: result.url,
    });

    res.json({
      success: true,
      data: result,
      traceId,
    });
  } catch (error) {
    childLogger.error("Upload request failed", error as Error, {
      body: req.body,
    });
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : "Upload failed",
      traceId,
    });
  }
});

// Error handling middleware
app.use(
  (
    err: any,
    req: express.Request,
    res: express.Response,
    next: express.NextFunction,
  ) => {
    const traceId = req.headers["x-trace-id"];
    const childLogger = logger.child({ traceId });
    childLogger.error("Unhandled error in middleware", err, {
      method: req.method,
      path: req.path,
    });

    res.status(500).json({
      success: false,
      error: "Internal server error",
      traceId,
    });
  },
);

// 404 handler
app.use((req, res) => {
  const traceId =
    req.headers["x-trace-id"] || Math.random().toString(36).substr(2, 9);
  const childLogger = logger.child({ traceId });

  childLogger.warn("Route not found", {
    method: req.method,
    path: req.path,
  });

  res.status(404).json({
    success: false,
    error: "Not found",
    traceId,
  });
});

app.listen(PORT, () => {
  logger.info("Video Tool API server started", {
    port: PORT,
    environment: process.env.NODE_ENV || "development",
    platforms: ["download", "edit", "upload"],
    endpoints: ["/api/health", "/api/download", "/api/edit", "/api/upload"],
  });
});
