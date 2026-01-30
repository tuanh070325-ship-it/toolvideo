"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createLogger = exports.PinoLogger = void 0;
const pino_1 = __importDefault(require("pino"));
class PinoLogger {
    logger;
    constructor(level = "info", format = "pretty") {
        this.logger = (0, pino_1.default)({
            level,
            transport: format === "pretty"
                ? {
                    target: "pino-pretty",
                    options: {
                        colorize: true,
                        translateTime: "HH:MM:ss Z",
                        ignore: "pid,hostname",
                    },
                }
                : undefined,
        });
    }
    debug(message, meta) {
        this.logger.debug(meta, message);
    }
    info(message, meta) {
        this.logger.info(meta, message);
    }
    warn(message, meta) {
        this.logger.warn(meta, message);
    }
    error(message, error, meta) {
        this.logger.error({ error, ...meta }, message);
    }
    child(context) {
        return new PinoLoggerChild(this.logger.child(context));
    }
}
exports.PinoLogger = PinoLogger;
class PinoLoggerChild {
    logger;
    constructor(logger) {
        this.logger = logger;
    }
    debug(message, meta) {
        this.logger.debug(meta, message);
    }
    info(message, meta) {
        this.logger.info(meta, message);
    }
    warn(message, meta) {
        this.logger.warn(meta, message);
    }
    error(message, error, meta) {
        this.logger.error({ error, ...meta }, message);
    }
    child(context) {
        return new PinoLoggerChild(this.logger.child(context));
    }
}
const createLogger = (level, format) => {
    return new PinoLogger(level, format);
};
exports.createLogger = createLogger;
//# sourceMappingURL=index.js.map