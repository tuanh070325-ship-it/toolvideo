'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Terminal, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Download,
  Copy,
  Trash2,
  Settings,
  Eye,
  EyeOff
} from 'lucide-react';
import clsx from 'clsx';

export interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'info' | 'success' | 'warning' | 'error' | 'debug';
  stage?: string;
  message: string;
  details?: Record<string, any>;
  duration?: number;
}

export interface PipelineStage {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  progress: number;
  message: string;
  startTime?: string;
  endTime?: string;
  durationSeconds?: number;
  error?: string;
}

export interface PipelineProgress {
  jobId: string;
  totalStages: number;
  completedStages: number;
  currentStage?: string;
  overallProgress: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  stages: Record<string, PipelineStage>;
  startTime?: string;
  endTime?: string;
  durationSeconds?: number;
  error?: string;
}

interface DebugLogPanelProps {
  logs: LogEntry[];
  pipelineProgress?: PipelineProgress;
  onClear?: () => void;
  className?: string;
  defaultExpanded?: boolean;
  debugMode?: boolean;
  onDebugModeChange?: (enabled: boolean) => void;
}

const levelIcons = {
  info: Terminal,
  success: CheckCircle,
  warning: AlertTriangle,
  error: XCircle,
  debug: Terminal,
};

const levelColors = {
  info: 'text-blue-400',
  success: 'text-green-400',
  warning: 'text-yellow-400',
  error: 'text-red-400',
  debug: 'text-gray-400',
};

const levelBgColors = {
  info: 'bg-blue-500/10',
  success: 'bg-green-500/10',
  warning: 'bg-yellow-500/10',
  error: 'bg-red-500/10',
  debug: 'bg-gray-500/10',
};

const stageStatusColors = {
  pending: 'bg-gray-500/20 text-gray-400',
  running: 'bg-blue-500/20 text-blue-400',
  completed: 'bg-green-500/20 text-green-400',
  failed: 'bg-red-500/20 text-red-400',
  skipped: 'bg-gray-500/20 text-gray-400',
};

function formatTime(date: Date): string {
  return date.toLocaleTimeString('vi-VN', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit',
    hour12: false 
  });
}

function formatDuration(seconds?: number): string {
  if (seconds === undefined || seconds === null) return '--';
  if (seconds < 1) return `${(seconds * 1000).toFixed(0)}ms`;
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}m ${secs}s`;
}

function LogEntryItem({ log, showDetails }: { log: LogEntry; showDetails: boolean }) {
  const [expanded, setExpanded] = useState(false);
  const Icon = levelIcons[log.level];
  
  return (
    <div 
      className={clsx(
        'px-3 py-2 border-l-2 transition-all',
        levelBgColors[log.level],
        {
          'border-blue-400': log.level === 'info',
          'border-green-400': log.level === 'success',
          'border-yellow-400': log.level === 'warning',
          'border-red-400': log.level === 'error',
          'border-gray-400': log.level === 'debug',
        }
      )}
    >
      <div className="flex items-start gap-2">
        <Icon className={clsx('w-4 h-4 mt-0.5 flex-shrink-0', levelColors[log.level])} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-gray-500 font-mono">
              {formatTime(log.timestamp)}
            </span>
            {log.stage && (
              <span className="text-xs px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300">
                {log.stage}
              </span>
            )}
            {log.duration !== undefined && (
              <span className="text-xs text-gray-500">
                <Clock className="w-3 h-3 inline mr-1" />
                {formatDuration(log.duration / 1000)}
              </span>
            )}
          </div>
          <p className={clsx('text-sm mt-1', levelColors[log.level])}>
            {log.message}
          </p>
          
          {/* Details section */}
          {showDetails && log.details && Object.keys(log.details).length > 0 && (
            <div className="mt-2">
              <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center gap-1 text-xs text-gray-400 hover:text-gray-300"
              >
                {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                Details
              </button>
              {expanded && (
                <pre className="mt-2 p-2 rounded bg-black/30 text-xs text-gray-300 overflow-x-auto">
                  {JSON.stringify(log.details, null, 2)}
                </pre>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PipelineProgressBar({ progress }: { progress: PipelineProgress }) {
  const stages = Object.entries(progress.stages || {});
  
  return (
    <div className="p-4 bg-black/20 rounded-xl border border-white/10">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-white">
            Job: {progress.jobId}
          </span>
          <span className={clsx(
            'px-2 py-0.5 rounded text-xs font-medium',
            {
              'bg-gray-500/20 text-gray-400': progress.status === 'pending',
              'bg-blue-500/20 text-blue-400': progress.status === 'running',
              'bg-green-500/20 text-green-400': progress.status === 'completed',
              'bg-red-500/20 text-red-400': progress.status === 'failed',
            }
          )}>
            {progress.status.toUpperCase()}
          </span>
        </div>
        <div className="flex items-center gap-3 text-sm text-gray-400">
          <span>{progress.completedStages}/{progress.totalStages} stages</span>
          {progress.durationSeconds && (
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {formatDuration(progress.durationSeconds)}
            </span>
          )}
        </div>
      </div>
      
      {/* Overall Progress */}
      <div className="mb-4">
        <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
          <span>Overall Progress</span>
          <span>{Math.round(progress.overallProgress)}%</span>
        </div>
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className={clsx(
              'h-full transition-all duration-500',
              {
                'bg-gradient-to-r from-purple-500 to-pink-500': progress.status === 'running',
                'bg-green-500': progress.status === 'completed',
                'bg-red-500': progress.status === 'failed',
                'bg-gray-600': progress.status === 'pending',
              }
            )}
            style={{ width: `${progress.overallProgress}%` }}
          />
        </div>
      </div>
      
      {/* Stages */}
      <div className="space-y-2">
        {stages.map(([key, stage]) => (
          <div key={key} className="flex items-center gap-3">
            {/* Stage indicator */}
            <div className={clsx(
              'w-24 px-2 py-1 rounded text-xs font-medium text-center truncate',
              stageStatusColors[stage.status]
            )}>
              {stage.name || key}
            </div>
            
            {/* Progress bar */}
            <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={clsx(
                  'h-full transition-all duration-300',
                  {
                    'bg-blue-500': stage.status === 'running',
                    'bg-green-500': stage.status === 'completed',
                    'bg-red-500': stage.status === 'failed',
                    'bg-gray-600': stage.status === 'pending' || stage.status === 'skipped',
                  }
                )}
                style={{ width: `${stage.progress}%` }}
              />
            </div>
            
            {/* Duration */}
            <span className="text-xs text-gray-500 w-16 text-right">
              {formatDuration(stage.durationSeconds)}
            </span>
          </div>
        ))}
      </div>
      
      {/* Error message */}
      {progress.error && (
        <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
          <p className="text-sm text-red-300">{progress.error}</p>
        </div>
      )}
    </div>
  );
}

export function DebugLogPanel({
  logs,
  pipelineProgress,
  onClear,
  className,
  defaultExpanded = true,
  debugMode = false,
  onDebugModeChange,
}: DebugLogPanelProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [showDebugLogs, setShowDebugLogs] = useState(debugMode);
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);
  
  // Filter logs based on debug mode
  const filteredLogs = showDebugLogs ? logs : logs.filter(l => l.level !== 'debug');
  
  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [filteredLogs.length, autoScroll]);
  
  const handleCopyLogs = () => {
    const logText = filteredLogs
      .map(l => `[${formatTime(l.timestamp)}] [${l.level.toUpperCase()}]${l.stage ? ` [${l.stage}]` : ''} ${l.message}`)
      .join('\n');
    navigator.clipboard.writeText(logText);
  };
  
  const handleDownloadLogs = () => {
    const logText = JSON.stringify(filteredLogs, null, 2);
    const blob = new Blob([logText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `logs_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className={clsx('rounded-xl bg-gray-900/50 border border-white/10 overflow-hidden', className)}>
      {/* Header */}
      <div 
        className="flex items-center justify-between px-4 py-3 bg-black/30 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          <Terminal className="w-5 h-5 text-purple-400" />
          <span className="font-medium text-white">Debug Logs</span>
          {filteredLogs.length > 0 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-purple-500/20 text-purple-300">
              {filteredLogs.length}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {expanded ? (
            <ChevronUp className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </div>
      
      {/* Content */}
      {expanded && (
        <div className="border-t border-white/10">
          {/* Toolbar */}
          <div className="flex items-center justify-between px-4 py-2 bg-black/20 border-b border-white/10">
            <div className="flex items-center gap-3">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowDebugLogs(!showDebugLogs);
                  onDebugModeChange?.(!showDebugLogs);
                }}
                className={clsx(
                  'flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-colors',
                  showDebugLogs
                    ? 'bg-purple-500/20 text-purple-300'
                    : 'bg-gray-700/50 text-gray-400 hover:text-gray-300'
                )}
              >
                {showDebugLogs ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
                Debug
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setAutoScroll(!autoScroll);
                }}
                className={clsx(
                  'flex items-center gap-1.5 px-2 py-1 rounded text-xs transition-colors',
                  autoScroll
                    ? 'bg-blue-500/20 text-blue-300'
                    : 'bg-gray-700/50 text-gray-400 hover:text-gray-300'
                )}
              >
                Auto-scroll
              </button>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleCopyLogs();
                }}
                className="p-1.5 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                title="Copy logs"
              >
                <Copy className="w-4 h-4" />
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDownloadLogs();
                }}
                className="p-1.5 rounded hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
                title="Download logs"
              >
                <Download className="w-4 h-4" />
              </button>
              {onClear && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onClear();
                  }}
                  className="p-1.5 rounded hover:bg-red-500/20 text-gray-400 hover:text-red-400 transition-colors"
                  title="Clear logs"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>
          
          {/* Pipeline Progress */}
          {pipelineProgress && (
            <div className="p-4 border-b border-white/10">
              <PipelineProgressBar progress={pipelineProgress} />
            </div>
          )}
          
          {/* Logs */}
          <div className="max-h-64 overflow-y-auto">
            {filteredLogs.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Terminal className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No logs yet</p>
              </div>
            ) : (
              <div className="divide-y divide-white/5">
                {filteredLogs.map((log) => (
                  <LogEntryItem key={log.id} log={log} showDetails={showDebugLogs} />
                ))}
                <div ref={logsEndRef} />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// Hook for managing logs
export function useDebugLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [pipelineProgress, setPipelineProgress] = useState<PipelineProgress | undefined>();
  
  const addLog = (
    level: LogEntry['level'],
    message: string,
    options?: { stage?: string; details?: Record<string, any>; duration?: number }
  ) => {
    const log: LogEntry = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      timestamp: new Date(),
      level,
      message,
      ...options,
    };
    setLogs(prev => [...prev, log]);
  };
  
  const clearLogs = () => setLogs([]);
  
  const info = (message: string, options?: { stage?: string; details?: Record<string, any> }) => 
    addLog('info', message, options);
    
  const success = (message: string, options?: { stage?: string; details?: Record<string, any>; duration?: number }) => 
    addLog('success', message, options);
    
  const warning = (message: string, options?: { stage?: string; details?: Record<string, any> }) => 
    addLog('warning', message, options);
    
  const error = (message: string, options?: { stage?: string; details?: Record<string, any> }) => 
    addLog('error', message, options);
    
  const debug = (message: string, options?: { stage?: string; details?: Record<string, any> }) => 
    addLog('debug', message, options);
  
  return {
    logs,
    pipelineProgress,
    setPipelineProgress,
    addLog,
    clearLogs,
    info,
    success,
    warning,
    error,
    debug,
  };
}

export default DebugLogPanel;
