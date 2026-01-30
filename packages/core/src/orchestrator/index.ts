import {
  Config,
  Logger,
  Storage,
  Queue,
  ProcessingJob,
  JobType,
  JobStatus,
} from "../types";

export class VideoToolOrchestrator {
  private config: Config;
  private logger: Logger;
  private storage: Storage;
  private queue: Queue;
  private isRunning = false;

  constructor(config: Config, logger: Logger, storage: Storage, queue: Queue) {
    this.config = config;
    this.logger = logger.child({ component: "Orchestrator" });
    this.storage = storage;
    this.queue = queue;
  }

  async start(): Promise<void> {
    if (this.isRunning) {
      this.logger.warn("Orchestrator is already running");
      return;
    }

    this.isRunning = true;
    this.logger.info("Starting video tool orchestrator");

    // Start worker processes
    const workers = [
      this.startWorker(JobType.DOWNLOAD, this.config.concurrency.downloads),
      this.startWorker(JobType.EDIT, this.config.concurrency.edits),
      this.startWorker(JobType.UPLOAD, this.config.concurrency.uploads),
    ];

    await Promise.all(workers);
    this.logger.info("All workers started");
  }

  async stop(): Promise<void> {
    if (!this.isRunning) {
      this.logger.warn("Orchestrator is not running");
      return;
    }

    this.isRunning = false;
    this.logger.info("Stopping video tool orchestrator");
  }

  async createJob(
    type: JobType,
    input: any,
    options: Record<string, any> = {},
  ): Promise<ProcessingJob> {
    const job: ProcessingJob = {
      id: this.generateId(),
      type,
      status: JobStatus.PENDING,
      input,
      options,
      progress: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    await this.queue.enqueue(job);
    this.logger.info("Job created", { jobId: job.id, type });
    return job;
  }

  async getJob(jobId: string): Promise<ProcessingJob | null> {
    return this.queue.getJob(jobId);
  }

  async listJobs(status?: JobStatus, limit = 50): Promise<ProcessingJob[]> {
    return this.queue.listJobs(status, limit);
  }

  private async startWorker(type: JobType, concurrency: number): Promise<void> {
    const workerLogger = this.logger.child({ worker: type });

    const workers = Array.from({ length: concurrency }, (_, i) =>
      this.runWorker(type, i, workerLogger),
    );

    await Promise.all(workers);
  }

  private async runWorker(
    type: JobType,
    workerId: number,
    logger: Logger,
  ): Promise<void> {
    logger.info(`Worker ${workerId} started for ${type}`);

    while (this.isRunning) {
      try {
        const job = await this.queue.dequeue(type);
        if (!job) {
          await this.sleep(1000);
          continue;
        }

        logger.info(`Processing job ${job.id}`, { workerId });
        await this.processJob(job, logger);
      } catch (error) {
        logger.error("Worker error", error as Error, { workerId, type });
        await this.sleep(5000);
      }
    }

    logger.info(`Worker ${workerId} stopped`);
  }

  private async processJob(job: ProcessingJob, logger: Logger): Promise<void> {
    try {
      await this.queue.updateStatus(job.id, JobStatus.RUNNING, 0);

      switch (job.type) {
        case JobType.DOWNLOAD:
          await this.processDownload(job, logger);
          break;
        case JobType.EDIT:
          await this.processEdit(job, logger);
          break;
        case JobType.UPLOAD:
          await this.processUpload(job, logger);
          break;
        default:
          throw new Error(`Unknown job type: ${job.type}`);
      }

      await this.queue.updateStatus(job.id, JobStatus.COMPLETED, 100);
      logger.info(`Job ${job.id} completed successfully`);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      await this.queue.updateStatus(job.id, JobStatus.FAILED, 0, errorMessage);
      logger.error(`Job ${job.id} failed`, error as Error);
    }
  }

  private async processDownload(
    job: ProcessingJob,
    logger: Logger,
  ): Promise<void> {
    // TODO: Implement download processing
    logger.info("Processing download", { jobId: job.id });
    await this.sleep(2000); // Simulate processing
  }

  private async processEdit(job: ProcessingJob, logger: Logger): Promise<void> {
    // TODO: Implement edit processing
    logger.info("Processing edit", { jobId: job.id });
    await this.sleep(3000); // Simulate processing
  }

  private async processUpload(
    job: ProcessingJob,
    logger: Logger,
  ): Promise<void> {
    // TODO: Implement upload processing
    logger.info("Processing upload", { jobId: job.id });
    await this.sleep(1500); // Simulate processing
  }

  private generateId(): string {
    return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => {
      const timer = global.setTimeout || setTimeout;
      timer(resolve, ms);
    });
  }
}
