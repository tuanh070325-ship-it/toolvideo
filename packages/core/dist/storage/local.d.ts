import type { Storage, Logger } from "../types";
export declare class LocalStorage implements Storage {
    private basePath;
    private logger;
    constructor(basePath: string, logger: Logger);
    put(key: string, data: Buffer | string, metadata?: Record<string, any>): Promise<string>;
    get(key: string): Promise<Buffer>;
    delete(key: string): Promise<void>;
    exists(key: string): Promise<boolean>;
    getUrl(key: string): Promise<string>;
    list(prefix?: string): Promise<string[]>;
    private readdirRecursive;
}
//# sourceMappingURL=local.d.ts.map