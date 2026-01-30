'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  Video,
  Settings,
  AlertCircle,
  Loader,
  Upload,
  BookOpen,
  Play,
  Scissors,
  Layers,
  Sparkles,
  CheckCircle,
  XCircle,
  Maximize2
} from 'lucide-react';
import toast from 'react-hot-toast';
import { apiClient } from '@/lib/api-client';
import { ReupVideoFeature } from '@/components/features/ReupVideoFeature';
import { StudioFeature } from '@/components/features/StudioFeature';
import { StoryVideoFeature } from '@/components/features/StoryVideoFeature';
import { SeriesFeature } from '@/components/features/SeriesFeature';
import { HighlightFeature } from '@/components/features/HighlightFeature';
import { SplitScreenFeature } from '@/components/features/SplitScreenFeature';
import { AspectRatioFeature } from '@/components/features/AspectRatioFeature';
import { TTSSettings } from '@/components/TTSSettings';
import { VideoPlayer } from '@/components/VideoPlayer';
import { EOAChatbot } from '@/components/EOAChatbot';
import clsx from 'clsx';

type TabKey = 'reup' | 'studio' | 'story' | 'series' | 'highlight' | 'merge' | 'aspect' | 'tts';

interface HealthStatus {
  api?: boolean;
  database?: boolean;
  redis?: boolean;
  storage?: boolean;
}

interface JobInfo {
  id: string;
  status: string;
  progress: number;
  current_step: string;
  output_url?: string;
  error_message?: string;
}

export default function HomePage() {
  const [selectedTab, setSelectedTab] = useState<TabKey>('reup');
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Video preview state
  const [currentJob, setCurrentJob] = useState<JobInfo | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    try {
      const status = await apiClient.getHealth();
      setHealthStatus(status);
      setHasError(false);
    } catch {
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  // Update video URL when job completes
  useEffect(() => {
    if (currentJob?.status === 'completed' && currentJob.output_url) {
      setVideoUrl(currentJob.output_url);
    }
  }, [currentJob]);

  const tabs = [
    { key: 'reup' as TabKey, label: 'Reup', icon: Upload, description: 'Tải và xử lý video từ URL với AI' },
    { key: 'studio' as TabKey, label: 'Studio', icon: Sparkles, description: 'Sáng tạo kịch bản & hình ảnh viral từ một chủ đề' },
    { key: 'story' as TabKey, label: 'Story', icon: BookOpen, description: 'Tạo video câu chuyện AI với âm thanh' },
    { key: 'series' as TabKey, label: 'Series', icon: Layers, description: 'Tạo series kể chuyện dài kỳ (3-10 tập)' },
    { key: 'highlight' as TabKey, label: 'Highlight', icon: Scissors, description: 'Trích xuất đoạn hay nhất từ video dài' },
    { key: 'merge' as TabKey, label: 'Split Screen', icon: Layers, description: 'Ghép 2 video split-screen' },
    { key: 'aspect' as TabKey, label: 'Tỉ lệ', icon: Maximize2, description: 'Chuyển đổi tỉ lệ khung hình' },
    { key: 'tts' as TabKey, label: 'TTS', icon: Settings, description: 'Cài đặt giọng nói AI (Edge, ViettelAI, FPT, ElevenLabs...)' },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900">
        <div className="text-center">
          <Loader className="w-12 h-12 mx-auto mb-4 text-purple-500 animate-spin" />
          <p className="text-lg font-semibold text-white">Đang tải...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="sticky top-0 z-40 border-b border-white/10 bg-gray-950/90 backdrop-blur-xl">
        <div className="max-w-[1400px] mx-auto px-6 py-5">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-500/30 via-purple-500/10 to-transparent border border-purple-500/30">
                <Video className="w-6 h-6 text-purple-300" />
              </div>
              <div>
                <h1 className="text-2xl font-semibold">Video Factory AI</h1>
                <p className="text-sm text-gray-400">Trung tâm xử lý video & AI assistant</p>
              </div>
            </div>

            {/* Health Status */}
            <div className="flex items-center gap-3">
              <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-gray-300 md:flex">
                <AlertCircle className="h-4 w-4" />
                API: {healthStatus && !hasError ? 'Online' : 'Offline'}
              </div>
              {healthStatus && !hasError ? (
                <div className="flex items-center gap-2 rounded-full bg-emerald-500/10 px-4 py-2 text-sm text-emerald-300">
                  <CheckCircle className="w-4 h-4" />
                  Online
                </div>
              ) : (
                <div className="flex items-center gap-2 rounded-full bg-red-500/10 px-4 py-2 text-sm text-red-300">
                  <XCircle className="w-4 h-4" />
                  Offline
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Split Screen */}
      <main className="mx-auto grid min-h-[calc(100vh-88px)] max-w-[1400px] grid-cols-1 gap-6 px-6 py-8 lg:grid-cols-[1.2fr_0.8fr]">
        {/* Left Panel - Settings/Features */}
        <div className="space-y-6">
          <div className="rounded-3xl border border-white/10 bg-white/5 p-4 shadow-xl shadow-black/20">
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  role="tab"
                  aria-selected={selectedTab === tab.key}
                  aria-controls={`tab-panel-${tab.key}`}
                  onClick={() => setSelectedTab(tab.key)}
                  className={clsx(
                    'group flex items-center gap-3 rounded-2xl border px-4 py-3 text-left transition-all',
                    selectedTab === tab.key
                      ? 'border-purple-500/50 bg-purple-500/20 text-white shadow-lg shadow-purple-500/10'
                      : 'border-white/10 bg-white/5 text-gray-300 hover:border-purple-500/30 hover:bg-white/10'
                  )}
                >
                  <div
                    className={clsx(
                      'flex h-9 w-9 items-center justify-center rounded-xl border',
                      selectedTab === tab.key
                        ? 'border-purple-400/60 bg-purple-500/30 text-purple-200'
                        : 'border-white/10 bg-white/5 text-gray-400 group-hover:text-purple-200'
                    )}
                  >
                    <tab.icon className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="text-sm font-semibold">{tab.label}</div>
                    <div className="text-xs text-gray-400">{tab.description}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl shadow-black/20">
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">Tùy chỉnh nhanh</h2>
                <p className="text-sm text-gray-400">
                  {tabs.find((t) => t.key === selectedTab)?.description}
                </p>
              </div>
              <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-gray-400">
                {selectedTab.toUpperCase()}
              </div>
            </div>

            <div
              role="tabpanel"
              id={`tab-panel-${selectedTab}`}
              className="space-y-6"
            >
              {selectedTab === 'reup' && <ReupVideoFeature />}
              {selectedTab === 'studio' && <StudioFeature />}
              {selectedTab === 'story' && <StoryVideoFeature />}
              {selectedTab === 'series' && <SeriesFeature />}
              {selectedTab === 'highlight' && <HighlightFeature />}
              {selectedTab === 'merge' && <SplitScreenFeature />}
              {selectedTab === 'aspect' && <AspectRatioFeature />}
              {selectedTab === 'tts' && <TTSSettings />}
            </div>
          </div>
        </div>

        {/* Right Panel - Video Preview */}
        <div className="flex flex-col gap-6">
          <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl shadow-black/20">
            <div className="flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-lg font-semibold">
                <Play className="w-5 h-5 text-purple-300" />
                Xem trước
              </h2>
              <span className="text-xs text-gray-400">Video output</span>
            </div>

            <div className="mt-4 overflow-hidden rounded-2xl border border-white/10 bg-black/40" style={{ minHeight: '360px' }}>
              <VideoPlayer
                src={videoUrl || undefined}
                title={currentJob?.id ? `Job: ${currentJob.id}` : 'Video Preview'}
                showDownload={!!videoUrl}
              />
            </div>

            {!videoUrl && (
              <div className="mt-4 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-gray-400">
                Video đã xử lý sẽ hiển thị tại đây trước khi tải xuống.
              </div>
            )}
          </div>

          {/* Job Status */}
          {currentJob && currentJob.status !== 'completed' && (
            <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl shadow-black/20">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium text-gray-300">Trạng thái xử lý</span>
                <span
                  className={clsx(
                    'px-3 py-1 rounded-full text-xs font-medium',
                    {
                      'bg-yellow-500/20 text-yellow-300': currentJob.status === 'pending',
                      'bg-blue-500/20 text-blue-300':
                        currentJob.status === 'processing' || currentJob.status === 'downloading',
                      'bg-green-500/20 text-green-300': currentJob.status === 'completed',
                      'bg-red-500/20 text-red-300': currentJob.status === 'failed',
                    }
                  )}
                >
                  {currentJob.status}
                </span>
              </div>

              <div className="h-2 bg-gray-700 rounded-full overflow-hidden mb-2">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                  style={{ width: `${currentJob.progress}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-400">{currentJob.current_step}</span>
                <span className="text-purple-400">{currentJob.progress}%</span>
              </div>

              {currentJob.error_message && (
                <div className="mt-3 p-3 rounded-lg bg-red-500/10 border border-red-500/30">
                  <p className="text-sm text-red-300">{currentJob.error_message}</p>
                </div>
              )}
            </div>
          )}

          {/* Quick Tips */}
          {!currentJob && !videoUrl && (
            <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-xl shadow-black/20">
              <h3 className="text-sm font-semibold text-blue-300 mb-2">💡 Mẹo sử dụng</h3>
              <ul className="text-xs text-gray-400 space-y-1">
                <li>• Nhập URL video từ YouTube, TikTok, Instagram...</li>
                <li>• Chọn các tùy chọn xử lý bên trái</li>
                <li>• Video đã xử lý sẽ hiển thị tại đây</li>
                <li>• Sử dụng EOA Chat (góc phải dưới) để tạo nội dung AI</li>
              </ul>
            </div>
          )}
        </div>
      </main>

      {/* EOA Chatbot - VIP Feature */}
      <EOAChatbot />
    </div>
  );
}
