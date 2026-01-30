"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LocalStorage = void 0;
const fs_1 = require("fs");
const path_1 = require("path");
class LocalStorage {
    basePath;
    logger;
    constructor(basePath, logger) {
        this.basePath = basePath;
        this.logger = logger.child({ component: "LocalStorage" });
    }
    async put(key, data, metadata) {
        const filePath = (0, path_1.join)(this.basePath, key);
        const dirPath = dirname(filePath);
        await fs_1.promises.mkdir(dirPath, { recursive: true });
        await fs_1.promises.writeFile(filePath, data);
        if (metadata) {
            const metadataPath = `${filePath}.meta`;
            await fs_1.promises.writeFile(metadataPath, JSON.stringify(metadata, null, 2));
        }
        this.logger.debug("File stored", { key, filePath, size: data.length });
        return filePath;
    }
    async get(key) {
        const filePath = (0, path_1.join)(this.basePath, key);
        try {
            const data = await fs_1.promises.readFile(filePath);
            this.logger.debug("File retrieved", { key, filePath });
            return data;
        }
        catch (error) {
            this.logger.error("Failed to retrieve file", error, { key });
            throw error;
        }
    }
    async delete(key) {
        const filePath = (0, path_1.join)(this.basePath, key);
        const metadataPath = `${filePath}.meta`;
        try {
            await Promise.all([
                fs_1.promises.unlink(filePath).catch(() => { }),
                fs_1.promises.unlink(metadataPath).catch(() => { }),
            ]);
            this.logger.debug("File deleted", { key });
        }
        catch (error) {
            this.logger.error("Failed to delete file", error, { key });
            throw error;
        }
    }
    async exists(key) {
        const filePath = (0, path_1.join)(this.basePath, key);
        try {
            await fs_1.promises.access(filePath);
            return true;
        }
        catch {
            return false;
        }
    }
    async getUrl(key) {
        return (0, path_1.join)(this.basePath, key);
    }
    async list(prefix) {
        const searchPath = prefix ? (0, path_1.join)(this.basePath, prefix) : this.basePath;
        try {
            const files = await this.readdirRecursive(searchPath, this.basePath);
            const result = files.filter((file) => !file.endsWith(".meta"));
            this.logger.debug("Files listed", { prefix, count: result.length });
            return result;
        }
        catch (error) {
            this.logger.error("Failed to list files", error, { prefix });
            throw error;
        }
    }
    async readdirRecursive(dirPath, basePath) {
        const entries = await fs_1.promises.readdir(dirPath, { withFileTypes: true });
        const files = [];
        for (const entry of entries) {
            const fullPath = (0, path_1.join)(dirPath, entry.name);
            const relativePath = fullPath.replace(basePath + "/", "");
            if (entry.isDirectory()) {
                const subFiles = await this.readdirRecursive(fullPath, basePath);
                files.push(...subFiles);
            }
            else {
                files.push(relativePath);
            }
        }
        return files;
    }
}
exports.LocalStorage = LocalStorage;
function dirname(path) {
    const parts = path.split(/[/\\]/);
    return parts.slice(0, -1).join("/");
}
//# sourceMappingURL=local.js.map