import type { Logger } from "../interfaces";
export declare class PinoLogger implements Logger {
    private logger;
    constructor(level?: string, format?: "json" | "pretty");
    debug(message: string, meta?: any): void;
    info(message: string, meta?: any): void;
    warn(message: string, meta?: any): void;
    error(message: string, error?: Error, meta?: any): void;
    child(context: Record<string, any>): Logger;
}
export declare const createLogger: (level?: string, format?: "json" | "pretty") => Logger;
//# sourceMappingURL=index.d.ts.map