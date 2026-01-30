export interface VideoMetadata {
    id: string;
    title: string;
    description?: string;
    duration: number;
    format: string;
    quality: string;
    size: number;
    platform: Platform;
    url: string;
    thumbnail?: string;
    tags?: string[];
    createdAt: Date;
    updatedAt: Date;
}
export interface VideoFile {
    path: string;
    name: string;
    extension: string;
    mimeType: string;
    size: number;
    metadata?: Partial<VideoMetadata>;
}
export interface ProcessingJob {
    id: string;
    type: JobType;
    status: JobStatus;
    input: VideoFile;
    output?: VideoFile;
    options: Record<string, any>;
    progress: number;
    error?: string;
    createdAt: Date;
    updatedAt: Date;
    completedAt?: Date;
}
export interface DownloadOptions {
    quality?: string;
    format?: string;
    subtitles?: boolean;
    metadata?: boolean;
    outputPath?: string;
}
export interface EditOptions {
    trim?: {
        start: number;
        end: number;
    };
    resize?: {
        width: number;
        height: number;
    };
    watermark?: {
        text?: string;
        image?: string;
        position: "top-left" | "top-right" | "bottom-left" | "bottom-right" | "center";
        opacity?: number;
    };
    audio?: {
        volume?: number;
        normalize?: boolean;
        replace?: string;
    };
}
export interface UploadOptions {
    title?: string;
    description?: string;
    tags?: string[];
    privacy?: "public" | "private" | "unlisted";
    schedule?: Date;
    thumbnail?: string;
}
export declare enum Platform {
    YOUTUBE = "youtube",
    TIKTOK = "tiktok",
    FACEBOOK = "facebook",
    INSTAGRAM = "instagram",
    TWITTER = "twitter",
    GENERIC = "generic"
}
export declare enum JobType {
    DOWNLOAD = "download",
    EDIT = "edit",
    UPLOAD = "upload",
    TRANSCODE = "transcode"
}
export declare enum JobStatus {
    PENDING = "pending",
    RUNNING = "running",
    COMPLETED = "completed",
    FAILED = "failed",
    CANCELLED = "cancelled"
}
export interface Logger {
    debug(message: string, meta?: any): void;
    info(message: string, meta?: any): void;
    warn(message: string, meta?: any): void;
    error(message: string, error?: Error, meta?: any): void;
    child(context: Record<string, any>): Logger;
}
export interface Queue {
    enqueue(job: ProcessingJob): Promise<void>;
    dequeue(type?: JobType): Promise<ProcessingJob | null>;
    updateStatus(jobId: string, status: JobStatus, progress?: number, error?: string): Promise<void>;
    getJob(jobId: string): Promise<ProcessingJob | null>;
    listJobs(status?: JobStatus, limit?: number): Promise<ProcessingJob[]>;
    clear(): Promise<void>;
}
export interface Storage {
    put(key: string, data: Buffer | string, metadata?: Record<string, any>): Promise<string>;
    get(key: string): Promise<Buffer>;
    delete(key: string): Promise<void>;
    exists(key: string): Promise<boolean>;
    getUrl(key: string): Promise<string>;
    list(prefix?: string): Promise<string[]>;
}
export interface PluginInterface {
    name: string;
    version: string;
    platform: string;
    type: "downloader" | "uploader" | "editor";
    enabled: boolean;
    config?: Record<string, any>;
    initialize(): Promise<void>;
    destroy(): Promise<void>;
}
export interface Plugin {
    name: string;
    version: string;
    platform: Platform;
    type: "downloader" | "uploader" | "editor";
    enabled: boolean;
    config?: Record<string, any>;
}
export interface Config {
    storage: {
        type: "local" | "s3";
        local?: {
            path: string;
        };
        s3?: {
            bucket: string;
            region: string;
            accessKeyId: string;
            secretAccessKey: string;
        };
    };
    queue: {
        type: "redis" | "memory";
        redis?: {
            host: string;
            port: number;
            password?: string;
        };
    };
    logging: {
        level: "debug" | "info" | "warn" | "error";
        format: "json" | "pretty";
    };
    plugins: {
        path: string;
        autoLoad: boolean;
    };
    concurrency: {
        downloads: number;
        edits: number;
        uploads: number;
    };
}
//# sourceMappingURL=types.d.ts.map