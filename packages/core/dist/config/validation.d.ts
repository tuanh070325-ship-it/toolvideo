import { z } from "zod";
export declare const VideoMetadataSchema: z.ZodObject<{
    id: z.ZodString;
    title: z.ZodString;
    description: z.ZodOptional<z.ZodString>;
    duration: z.ZodNumber;
    format: z.ZodString;
    quality: z.ZodString;
    size: z.ZodNumber;
    platform: z.ZodEnum<["youtube", "tiktok", "facebook", "instagram", "twitter", "generic"]>;
    url: z.ZodString;
    thumbnail: z.ZodOptional<z.ZodString>;
    tags: z.ZodOptional<z.ZodArray<z.ZodString, "many">>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
}, "strip", z.ZodTypeAny, {
    id: string;
    title: string;
    duration: number;
    format: string;
    quality: string;
    size: number;
    platform: "youtube" | "tiktok" | "facebook" | "instagram" | "twitter" | "generic";
    url: string;
    createdAt: Date;
    updatedAt: Date;
    description?: string | undefined;
    thumbnail?: string | undefined;
    tags?: string[] | undefined;
}, {
    id: string;
    title: string;
    duration: number;
    format: string;
    quality: string;
    size: number;
    platform: "youtube" | "tiktok" | "facebook" | "instagram" | "twitter" | "generic";
    url: string;
    createdAt: Date;
    updatedAt: Date;
    description?: string | undefined;
    thumbnail?: string | undefined;
    tags?: string[] | undefined;
}>;
export declare const VideoFileSchema: z.ZodObject<{
    path: z.ZodString;
    name: z.ZodString;
    extension: z.ZodString;
    mimeType: z.ZodString;
    size: z.ZodNumber;
    metadata: any;
}, "strip", z.ZodTypeAny, {
    [x: string]: any;
    path?: unknown;
    name?: unknown;
    extension?: unknown;
    mimeType?: unknown;
    size?: unknown;
    metadata?: unknown;
}, {
    [x: string]: any;
    path?: unknown;
    name?: unknown;
    extension?: unknown;
    mimeType?: unknown;
    size?: unknown;
    metadata?: unknown;
}>;
export declare const ProcessingJobSchema: z.ZodObject<{
    id: z.ZodString;
    type: z.ZodEnum<["download", "edit", "upload", "transcode"]>;
    status: z.ZodEnum<["pending", "running", "completed", "failed", "cancelled"]>;
    input: z.ZodObject<{
        path: z.ZodString;
        name: z.ZodString;
        extension: z.ZodString;
        mimeType: z.ZodString;
        size: z.ZodNumber;
        metadata: any;
    }, "strip", z.ZodTypeAny, {
        [x: string]: any;
        path?: unknown;
        name?: unknown;
        extension?: unknown;
        mimeType?: unknown;
        size?: unknown;
        metadata?: unknown;
    }, {
        [x: string]: any;
        path?: unknown;
        name?: unknown;
        extension?: unknown;
        mimeType?: unknown;
        size?: unknown;
        metadata?: unknown;
    }>;
    output: z.ZodOptional<z.ZodObject<{
        path: z.ZodString;
        name: z.ZodString;
        extension: z.ZodString;
        mimeType: z.ZodString;
        size: z.ZodNumber;
        metadata: any;
    }, "strip", z.ZodTypeAny, {
        [x: string]: any;
        path?: unknown;
        name?: unknown;
        extension?: unknown;
        mimeType?: unknown;
        size?: unknown;
        metadata?: unknown;
    }, {
        [x: string]: any;
        path?: unknown;
        name?: unknown;
        extension?: unknown;
        mimeType?: unknown;
        size?: unknown;
        metadata?: unknown;
    }>>;
    options: z.ZodRecord<z.ZodString, z.ZodAny>;
    progress: z.ZodNumber;
    error: z.ZodOptional<z.ZodString>;
    createdAt: z.ZodDate;
    updatedAt: z.ZodDate;
    completedAt: z.ZodOptional<z.ZodDate>;
}, "strip", z.ZodTypeAny, {
    id: string;
    options: Record<string, any>;
    type: "download" | "edit" | "upload" | "transcode";
    status: "pending" | "running" | "completed" | "failed" | "cancelled";
    createdAt: Date;
    updatedAt: Date;
    input: {
        [x: string]: any;
        path?: unknown;
        name?: unknown;
        extension?: unknown;
        mimeType?: unknown;
        size?: unknown;
        metadata?: unknown;
    };
    progress: number;
    error?: string | undefined;
    output?: {
        [x: string]: any;
        path?: unknown;
        name?: unknown;
        extension?: unknown;
        mimeType?: unknown;
        size?: unknown;
        metadata?: unknown;
    } | undefined;
    completedAt?: Date | undefined;
}, {
    id: string;
    options: Record<string, any>;
    type: "download" | "edit" | "upload" | "transcode";
    status: "pending" | "running" | "completed" | "failed" | "cancelled";
    createdAt: Date;
    updatedAt: Date;
    input: {
        [x: string]: any;
        path?: unknown;
        name?: unknown;
        extension?: unknown;
        mimeType?: unknown;
        size?: unknown;
        metadata?: unknown;
    };
    progress: number;
    error?: string | undefined;
    output?: {
        [x: string]: any;
        path?: unknown;
        name?: unknown;
        extension?: unknown;
        mimeType?: unknown;
        size?: unknown;
        metadata?: unknown;
    } | undefined;
    completedAt?: Date | undefined;
}>;
//# sourceMappingURL=validation.d.ts.map