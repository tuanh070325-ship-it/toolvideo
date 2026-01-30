"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ProcessingJobSchema = exports.VideoFileSchema = exports.VideoMetadataSchema = void 0;
const zod_1 = require("zod");
const PlatformSchema = zod_1.z.enum([
    "youtube",
    "tiktok",
    "facebook",
    "instagram",
    "twitter",
    "generic",
]);
const JobTypeSchema = zod_1.z.enum(["download", "edit", "upload", "transcode"]);
const JobStatusSchema = zod_1.z.enum([
    "pending",
    "running",
    "completed",
    "failed",
    "cancelled",
]);
exports.VideoMetadataSchema = zod_1.z.object({
    id: zod_1.z.string(),
    title: zod_1.z.string(),
    description: zod_1.z.string().optional(),
    duration: zod_1.z.number(),
    format: zod_1.z.string(),
    quality: zod_1.z.string(),
    size: zod_1.z.number(),
    platform: PlatformSchema,
    url: zod_1.z.string(),
    thumbnail: zod_1.z.string().optional(),
    tags: zod_1.z.array(zod_1.z.string()).optional(),
    createdAt: zod_1.z.date(),
    updatedAt: zod_1.z.date(),
});
exports.VideoFileSchema = zod_1.z.object({
    path: zod_1.z.string(),
    name: zod_1.z.string(),
    extension: zod_1.z.string(),
    mimeType: zod_1.z.string(),
    size: zod_1.z.number(),
    metadata: zod_1.z.partial(exports.VideoMetadataSchema).optional(),
});
exports.ProcessingJobSchema = zod_1.z.object({
    id: zod_1.z.string(),
    type: JobTypeSchema,
    status: JobStatusSchema,
    input: exports.VideoFileSchema,
    output: exports.VideoFileSchema.optional(),
    options: zod_1.z.record(zod_1.z.any()),
    progress: zod_1.z.number(),
    error: zod_1.z.string().optional(),
    createdAt: zod_1.z.date(),
    updatedAt: zod_1.z.date(),
    completedAt: zod_1.z.date().optional(),
});
//# sourceMappingURL=validation.js.map