import { spawn } from "child_process";
import { promises as fs } from "fs";
import { join, dirname } from "path";
import {
  VideoFile,
  VideoMetadata,
  Platform,
  DownloadOptions,
  DownloaderPlugin,
} from "@video-tool/core";

export class YouTubeDownloader implements DownloaderPlugin {
  name = "youtube-downloader";
  platform = Platform.YOUTUBE;

  canHandle(url: string): boolean {
    return url.includes("youtube.com") || url.includes("youtu.be");
  }

  async download(url: string, options?: DownloadOptions): Promise<VideoFile> {
    const outputPath = options?.outputPath || "./downloads";
    const quality = options?.quality || "best";
    const format = options?.format || "mp4";

    await fs.mkdir(outputPath, { recursive: true });

    const filename = `youtube_${Date.now()}.${format}`;
    const filePath = join(outputPath, filename);

    const args = [
      "--format",
      `${quality}[ext=${format}]/best[ext=${format}]/best`,
      "--output",
      filePath,
      "--no-playlist",
      url,
    ];

    if (options?.subtitles) {
      args.push("--write-subs", "--write-auto-subs");
    }

    if (options?.metadata) {
      args.push("--embed-metadata");
    }

    return new Promise((resolve, reject) => {
      const process = spawn("yt-dlp", args);

      let stderr = "";
      process.stderr?.on("data", (data) => {
        stderr += data.toString();
      });

      process.on("close", async (code) => {
        if (code === 0) {
          try {
            const stats = await fs.stat(filePath);
            const videoFile: VideoFile = {
              path: filePath,
              name: filename,
              extension: format,
              mimeType: `video/${format}`,
              size: stats.size,
              metadata: await this.extractMetadata(filePath),
            };
            resolve(videoFile);
          } catch (error) {
            reject(error);
          }
        } else {
          reject(new Error(`yt-dlp failed with code ${code}: ${stderr}`));
        }
      });

      process.on("error", reject);
    });
  }

  async getMetadata(url: string): Promise<VideoMetadata> {
    const args = ["--dump-json", "--no-playlist", url];

    return new Promise((resolve, reject) => {
      const process = spawn("yt-dlp", args);

      let stdout = "";
      let stderr = "";

      process.stdout?.on("data", (data) => {
        stdout += data.toString();
      });

      process.stderr?.on("data", (data) => {
        stderr += data.toString();
      });

      process.on("close", (code) => {
        if (code === 0) {
          try {
            const data = JSON.parse(stdout);
            const metadata: VideoMetadata = {
              id: data.id,
              title: data.title,
              description: data.description,
              duration: data.duration,
              format: data.format,
              quality: data.resolution || "unknown",
              size: parseInt(data.filesize) || 0,
              platform: Platform.YOUTUBE,
              url: data.webpage_url,
              thumbnail: data.thumbnail,
              tags: data.tags,
              createdAt: new Date(data.upload_date),
              updatedAt: new Date(),
            };
            resolve(metadata);
          } catch (error) {
            reject(error);
          }
        } else {
          reject(
            new Error(`yt-dlp metadata failed with code ${code}: ${stderr}`),
          );
        }
      });

      process.on("error", reject);
    });
  }

  private async extractMetadata(
    filePath: string,
  ): Promise<Partial<VideoMetadata>> {
    // Use ffprobe to extract metadata
    const args = [
      "-v",
      "quiet",
      "-print_format",
      "json",
      "-show_format",
      "-show_streams",
      filePath,
    ];

    return new Promise((resolve, reject) => {
      const process = spawn("ffprobe", args);

      let stdout = "";
      process.stdout?.on("data", (data) => {
        stdout += data.toString();
      });

      process.on("close", (code) => {
        if (code === 0) {
          try {
            const data = JSON.parse(stdout);
            const videoStream = data.streams.find(
              (s: any) => s.codec_type === "video",
            );
            const audioStream = data.streams.find(
              (s: any) => s.codec_type === "audio",
            );

            resolve({
              duration: parseFloat(data.format.duration) || 0,
              format: data.format.format_name,
              size: parseInt(data.format.size) || 0,
              quality: `${videoStream?.width || 0}x${videoStream?.height || 0}`,
            });
          } catch (error) {
            resolve({});
          }
        } else {
          resolve({});
        }
      });

      process.on("error", () => {
        resolve({});
      });
    });
  }
}
