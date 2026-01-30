"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.loadConfig = void 0;
const getEnvVar = (key, defaultValue) => {
    const value = process.env[key];
    if (value === undefined) {
        if (defaultValue !== undefined)
            return defaultValue;
        throw new Error(`Environment variable ${key} is required`);
    }
    return value;
};
const getEnvNumber = (key, defaultValue) => {
    const value = process.env[key];
    if (value === undefined) {
        if (defaultValue !== undefined)
            return defaultValue;
        throw new Error(`Environment variable ${key} is required`);
    }
    const parsed = parseInt(value, 10);
    if (isNaN(parsed)) {
        throw new Error(`Environment variable ${key} must be a number`);
    }
    return parsed;
};
const loadConfig = () => ({
    storage: {
        type: process.env.STORAGE_TYPE || "local",
        local: process.env.STORAGE_TYPE === "local"
            ? {
                path: getEnvVar("STORAGE_LOCAL_PATH", "./data"),
            }
            : undefined,
        s3: process.env.STORAGE_TYPE === "s3"
            ? {
                bucket: getEnvVar("AWS_S3_BUCKET"),
                region: getEnvVar("AWS_REGION"),
                accessKeyId: getEnvVar("AWS_ACCESS_KEY_ID"),
                secretAccessKey: getEnvVar("AWS_SECRET_ACCESS_KEY"),
            }
            : undefined,
    },
    queue: {
        type: process.env.QUEUE_TYPE || "memory",
        redis: process.env.QUEUE_TYPE === "redis"
            ? {
                host: getEnvVar("REDIS_HOST", "localhost"),
                port: getEnvNumber("REDIS_PORT", 6379),
                password: process.env.REDIS_PASSWORD,
            }
            : undefined,
    },
    logging: {
        level: process.env.LOG_LEVEL || "info",
        format: process.env.LOG_FORMAT || "pretty",
    },
    plugins: {
        path: getEnvVar("PLUGINS_PATH", "./plugins"),
        autoLoad: process.env.PLUGINS_AUTO_LOAD !== "false",
    },
    concurrency: {
        downloads: getEnvNumber("CONCURRENCY_DOWNLOADS", 3),
        edits: getEnvNumber("CONCURRENCY_EDITS", 2),
        uploads: getEnvNumber("CONCURRENCY_UPLOADS", 2),
    },
});
exports.loadConfig = loadConfig;
//# sourceMappingURL=env.js.map