FROM node:20-alpine

# Install FFmpeg and yt-dlp
RUN apk add --no-cache \
    ffmpeg \
    python3 \
    py3-pip \
    && pip3 install --no-cache-dir yt-dlp

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY packages/ ./packages/

# Install dependencies
RUN npm ci

# Build packages
RUN npm run build

# Create data directory
RUN mkdir -p /app/data

# Environment variables
ENV NODE_ENV=production
ENV STORAGE_LOCAL_PATH=/app/data
PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/api/health || exit 1

# Expose port
EXPOSE 3000

# Start the API server
CMD ["node", "packages/api/dist/server.js"]