import {
  VideoFile,
  VideoMetadata,
  Platform,
  UploadOptions,
} from "@video-tool/core";

export interface UploaderPlugin {
  name: string;
  platform: Platform;
  authenticate(credentials: Record<string, string>): Promise<boolean>;
  upload(video: VideoFile, options?: UploadOptions): Promise<UploadResult>;
  getUploadStatus(uploadId: string): Promise<UploadStatus>;
}

export interface UploadResult {
  id: string;
  url: string;
  platform: Platform;
  status: UploadStatus;
  metadata?: Partial<VideoMetadata>;
}

export enum UploadStatus {
  PENDING = "pending",
  UPLOADING = "uploading",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

export class VideoUploader {
  private plugins: Map<Platform, UploaderPlugin[]> = new Map();
  private credentials: Map<Platform, Record<string, string>> = new Map();

  constructor() {
    this.initializePlugins();
  }

  registerPlugin(plugin: UploaderPlugin): void {
    const existing = this.plugins.get(plugin.platform) || [];
    existing.push(plugin);
    this.plugins.set(plugin.platform, existing);
  }

  setCredentials(
    platform: Platform,
    credentials: Record<string, string>,
  ): void {
    this.credentials.set(platform, credentials);
  }

  async upload(
    video: VideoFile,
    platform: Platform,
    options?: UploadOptions,
  ): Promise<UploadResult> {
    const plugins = this.plugins.get(platform) || [];
    const credentials = this.credentials.get(platform);

    if (plugins.length === 0) {
      throw new Error(`No upload plugins available for platform: ${platform}`);
    }

    if (!credentials) {
      throw new Error(`No credentials configured for platform: ${platform}`);
    }

    // Try each plugin until one succeeds
    for (const plugin of plugins) {
      try {
        const isAuthenticated = await plugin.authenticate(credentials);
        if (!isAuthenticated) {
          console.warn(`Plugin ${plugin.name} authentication failed`);
          continue;
        }

        return await plugin.upload(video, options);
      } catch (error) {
        console.warn(`Plugin ${plugin.name} failed:`, error);
        continue;
      }
    }

    throw new Error(`All upload plugins failed for platform: ${platform}`);
  }

  async getUploadStatus(
    platform: Platform,
    uploadId: string,
  ): Promise<UploadStatus> {
    const plugins = this.plugins.get(platform) || [];

    for (const plugin of plugins) {
      try {
        return await plugin.getUploadStatus(uploadId);
      } catch (error) {
        console.warn(`Plugin ${plugin.name} status check failed:`, error);
        continue;
      }
    }

    throw new Error(`Failed to get upload status for: ${uploadId}`);
  }

  getSupportedPlatforms(): Platform[] {
    return Array.from(this.plugins.keys());
  }

  private initializePlugins(): void {
    // Plugins will be loaded here
    // For now, we'll register them manually in the index.ts
  }
}
