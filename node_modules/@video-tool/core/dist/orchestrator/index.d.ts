import { Config, Logger, Storage, Queue, ProcessingJob, JobType, JobStatus } from "../types";
export declare class VideoToolOrchestrator {
    private config;
    private logger;
    private storage;
    private queue;
    private isRunning;
    constructor(config: Config, logger: Logger, storage: Storage, queue: Queue);
    start(): Promise<void>;
    stop(): Promise<void>;
    createJob(type: JobType, input: any, options?: Record<string, any>): Promise<ProcessingJob>;
    getJob(jobId: string): Promise<ProcessingJob | null>;
    listJobs(status?: JobStatus, limit?: number): Promise<ProcessingJob[]>;
    private startWorker;
    private runWorker;
    private processJob;
    private processDownload;
    private processEdit;
    private processUpload;
    private generateId;
    private sleep;
}
//# sourceMappingURL=index.d.ts.map