import { promises as fs } from "fs";
import { join } from "path";
import type { Storage, Logger } from "../types";

export class LocalStorage implements Storage {
  private basePath: string;
  private logger: Logger;

  constructor(basePath: string, logger: Logger) {
    this.basePath = basePath;
    this.logger = logger.child({ component: "LocalStorage" });
  }

  async put(
    key: string,
    data: Buffer | string,
    metadata?: Record<string, any>,
  ): Promise<string> {
    const filePath = join(this.basePath, key);
    const dirPath = dirname(filePath);

    await fs.mkdir(dirPath, { recursive: true });
    await fs.writeFile(filePath, data);

    if (metadata) {
      const metadataPath = `${filePath}.meta`;
      await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2));
    }

    this.logger.debug("File stored", { key, filePath, size: data.length });
    return filePath;
  }

  async get(key: string): Promise<Buffer> {
    const filePath = join(this.basePath, key);
    try {
      const data = await fs.readFile(filePath);
      this.logger.debug("File retrieved", { key, filePath });
      return data;
    } catch (error) {
      this.logger.error("Failed to retrieve file", error as Error, { key });
      throw error;
    }
  }

  async delete(key: string): Promise<void> {
    const filePath = join(this.basePath, key);
    const metadataPath = `${filePath}.meta`;

    try {
      await Promise.all([
        fs.unlink(filePath).catch(() => {}),
        fs.unlink(metadataPath).catch(() => {}),
      ]);

      this.logger.debug("File deleted", { key });
    } catch (error) {
      this.logger.error("Failed to delete file", error as Error, { key });
      throw error;
    }
  }

  async exists(key: string): Promise<boolean> {
    const filePath = join(this.basePath, key);
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  async getUrl(key: string): Promise<string> {
    return join(this.basePath, key);
  }

  async list(prefix?: string): Promise<string[]> {
    const searchPath = prefix ? join(this.basePath, prefix) : this.basePath;

    try {
      const files = await this.readdirRecursive(searchPath, this.basePath);
      const result = files.filter((file) => !file.endsWith(".meta"));

      this.logger.debug("Files listed", { prefix, count: result.length });
      return result;
    } catch (error) {
      this.logger.error("Failed to list files", error as Error, { prefix });
      throw error;
    }
  }

  private async readdirRecursive(
    dirPath: string,
    basePath: string,
  ): Promise<string[]> {
    const entries = await fs.readdir(dirPath, { withFileTypes: true });
    const files: string[] = [];

    for (const entry of entries) {
      const fullPath = join(dirPath, entry.name);
      const relativePath = fullPath.replace(basePath + "/", "");

      if (entry.isDirectory()) {
        const subFiles = await this.readdirRecursive(fullPath, basePath);
        files.push(...subFiles);
      } else {
        files.push(relativePath);
      }
    }

    return files;
  }
}

function dirname(path: string): string {
  const parts = path.split(/[/\\]/);
  return parts.slice(0, -1).join("/");
}
