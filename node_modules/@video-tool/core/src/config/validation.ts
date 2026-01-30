import { z } from "zod";

const PlatformSchema = z.enum([
  "youtube",
  "tiktok",
  "facebook",
  "instagram",
  "twitter",
  "generic",
]);

const JobTypeSchema = z.enum(["download", "edit", "upload", "transcode"]);

const JobStatusSchema = z.enum([
  "pending",
  "running",
  "completed",
  "failed",
  "cancelled",
]);

export const VideoMetadataSchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().optional(),
  duration: z.number(),
  format: z.string(),
  quality: z.string(),
  size: z.number(),
  platform: PlatformSchema,
  url: z.string(),
  thumbnail: z.string().optional(),
  tags: z.array(z.string()).optional(),
  createdAt: z.date(),
  updatedAt: z.date(),
});

export const VideoFileSchema = z.object({
  path: z.string(),
  name: z.string(),
  extension: z.string(),
  mimeType: z.string(),
  size: z.number(),
  metadata: z.partial(VideoMetadataSchema).optional(),
});

export const ProcessingJobSchema = z.object({
  id: z.string(),
  type: JobTypeSchema,
  status: JobStatusSchema,
  input: VideoFileSchema,
  output: VideoFileSchema.optional(),
  options: z.record(z.any()),
  progress: z.number(),
  error: z.string().optional(),
  createdAt: z.date(),
  updatedAt: z.date(),
  completedAt: z.date().optional(),
});
