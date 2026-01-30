import {
  VideoToolOrchestrator,
  loadConfig,
  createLogger,
  LocalStorage,
} from "@video-tool/core";
import { VideoDownloader } from "./downloader";
import { YouTubeDownloader } from "./platforms/youtube";

export { VideoDownloader, YouTubeDownloader };
export * from "./downloader";
export * from "./platforms/youtube";

// Create main downloader instance with all plugins
const config = loadConfig();
const logger = createLogger(config.logging.level, config.logging.format);
const storage = new LocalStorage(config.storage.local!.path, logger);
const downloader = new VideoDownloader();

// Register plugins
downloader.registerPlugin(new YouTubeDownloader());

export default downloader;
