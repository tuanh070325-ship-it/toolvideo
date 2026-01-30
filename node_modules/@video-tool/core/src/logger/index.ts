import pino from "pino";
import type { Logger } from "../interfaces";

export class PinoLogger implements Logger {
  private logger: pino.Logger;

  constructor(level: string = "info", format: "json" | "pretty" = "pretty") {
    this.logger = pino({
      level,
      transport:
        format === "pretty"
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

  debug(message: string, meta?: any): void {
    this.logger.debug(meta, message);
  }

  info(message: string, meta?: any): void {
    this.logger.info(meta, message);
  }

  warn(message: string, meta?: any): void {
    this.logger.warn(meta, message);
  }

  error(message: string, error?: Error, meta?: any): void {
    this.logger.error({ error, ...meta }, message);
  }

  child(context: Record<string, any>): Logger {
    return new PinoLoggerChild(this.logger.child(context));
  }
}

class PinoLoggerChild implements Logger {
  private logger: pino.Logger;

  constructor(logger: pino.Logger) {
    this.logger = logger;
  }

  debug(message: string, meta?: any): void {
    this.logger.debug(meta, message);
  }

  info(message: string, meta?: any): void {
    this.logger.info(meta, message);
  }

  warn(message: string, meta?: any): void {
    this.logger.warn(meta, message);
  }

  error(message: string, error?: Error, meta?: any): void {
    this.logger.error({ error, ...meta }, message);
  }

  child(context: Record<string, any>): Logger {
    return new PinoLoggerChild(this.logger.child(context));
  }
}

export const createLogger = (
  level?: string,
  format?: "json" | "pretty",
): Logger => {
  return new PinoLogger(level, format);
};
