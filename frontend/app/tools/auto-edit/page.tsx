'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/shared'
import { apiClient } from '@/lib/api/client'

export default function AutoEditPage() {
    const [videoUrl, setVideoUrl] = useState('')
    const [activeTab, setActiveTab] = useState<'silence' | 'trim' | 'analyze'>('silence')
    
    // Silence removal settings
    const [thresholdDb, setThresholdDb] = useState(-30)
    const [minSilence, setMinSilence] = useState(0.5)
    const [margin, setMargin] = useState(0.1)
    const [speedUpSilence, setSpeedUpSilence] = useState<number | null>(null)
    
    // Smart trim settings
    const [targetDuration, setTargetDuration] = useState(60)
    const [keepStart, setKeepStart] = useState(true)
    const [keepEnd, setKeepEnd] = useState(true)
    
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<any>(null)
    const [analysisResult, setAnalysisResult] = useState<any>(null)
    const [error, setError] = useState('')

    const handleAnalyze = async () => {
        if (!videoUrl.trim()) {
            setError('Vui lòng nhập URL video')
            return
        }

        setLoading(true)
        setError('')
        setAnalysisResult(null)

        try {
            const response = await apiClient.post('/tools/auto-edit/analyze', null, {
                params: { video_url: videoUrl.trim() }
            })
            setAnalysisResult(response.data)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Phân tích thất bại')
        } finally {
            setLoading(false)
        }
    }

    const handleRemoveSilence = async () => {
        if (!videoUrl.trim()) {
            setError('Vui lòng nhập URL video')
            return
        }

        setLoading(true)
        setError('')
        setResult(null)

        try {
            const response = await apiClient.post('/tools/auto-edit/remove-silence', {
                video_url: videoUrl.trim(),
                threshold_db: thresholdDb,
                min_silence_duration: minSilence,
                margin,
                speed_up_silence: speedUpSilence,
                remove_silence: !speedUpSilence
            })

            setResult(response.data)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Cắt im lặng thất bại')
        } finally {
            setLoading(false)
        }
    }

    const handleSmartTrim = async () => {
        if (!videoUrl.trim()) {
            setError('Vui lòng nhập URL video')
            return
        }

        setLoading(true)
        setError('')
        setResult(null)

        try {
            const response = await apiClient.post('/tools/auto-edit/smart-trim', {
                video_url: videoUrl.trim(),
                target_duration: targetDuration,
                keep_start: keepStart,
                keep_end: keepEnd
            })

            setResult(response.data)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Cắt gọn thất bại')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-6xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/tools" className="text-gray-500 hover:text-gray-700">
                        ← Quay lại
                    </Link>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
                    <div className="flex items-center gap-3 mb-4">
                        <span className="text-4xl">✂️</span>
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">Chỉnh Sửa Video Tự Động</h1>
                            <p className="text-gray-500">Nguồn: Auto-Editor</p>
                        </div>
                    </div>
                    <p className="text-gray-600">
                        Tự động phân tích âm thanh, cắt bỏ đoạn im lặng, tăng tốc phần không có lời,
                        và cắt gọn video thông minh để tạo nội dung hấp dẫn hơn.
                    </p>
                </div>

                {/* Video URL Input */}
                <Card className="mb-6">
                    <CardContent className="pt-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                URL Video nguồn *
                            </label>
                            <Input
                                placeholder="https://www.tiktok.com/@user/video/123 hoặc YouTube, Instagram..."
                                value={videoUrl}
                                onChange={(e) => setVideoUrl(e.target.value)}
                                disabled={loading}
                            />
                        </div>
                    </CardContent>
                </Card>

                {/* Tabs */}
                <div className="flex border-b border-gray-200 mb-6">
                    <button
                        onClick={() => setActiveTab('analyze')}
                        className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                            activeTab === 'analyze'
                                ? 'border-green-500 text-green-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        📊 Phân tích
                    </button>
                    <button
                        onClick={() => setActiveTab('silence')}
                        className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                            activeTab === 'silence'
                                ? 'border-green-500 text-green-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        🔇 Cắt Im lặng
                    </button>
                    <button
                        onClick={() => setActiveTab('trim')}
                        className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
                            activeTab === 'trim'
                                ? 'border-green-500 text-green-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        ⏱️ Cắt Gọn
                    </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Form */}
                    <div className="lg:col-span-2">
                        <Card>
                            <CardHeader>
                                <CardTitle>
                                    {activeTab === 'analyze' && '📊 Phân tích Âm thanh'}
                                    {activeTab === 'silence' && '🔇 Cắt bỏ Im lặng'}
                                    {activeTab === 'trim' && '⏱️ Cắt Gọn Thông minh'}
                                </CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                {/* Analyze Tab */}
                                {activeTab === 'analyze' && (
                                    <>
                                        <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                                            <p className="text-blue-700 text-sm">
                                                Phân tích video để xem tỷ lệ im lặng vs lời nói, 
                                                giúp bạn quyết định cách xử lý phù hợp.
                                            </p>
                                        </div>

                                        <Button
                                            className="w-full bg-green-600 hover:bg-green-700"
                                            onClick={handleAnalyze}
                                            disabled={loading}
                                        >
                                            {loading ? '⏳ Đang phân tích...' : '📊 Phân tích Video'}
                                        </Button>

                                        {analysisResult && analysisResult.success && (
                                            <div className="space-y-4 mt-4">
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div className="bg-gray-50 p-4 rounded-lg text-center">
                                                        <p className="text-2xl font-bold text-gray-900">
                                                            {Math.round(analysisResult.duration)}s
                                                        </p>
                                                        <p className="text-sm text-gray-500">Tổng thời lượng</p>
                                                    </div>
                                                    <div className="bg-gray-50 p-4 rounded-lg text-center">
                                                        <p className="text-2xl font-bold text-gray-900">
                                                            {analysisResult.silences?.length || 0}
                                                        </p>
                                                        <p className="text-sm text-gray-500">Đoạn im lặng</p>
                                                    </div>
                                                </div>

                                                <div className="grid grid-cols-2 gap-4">
                                                    <div className="bg-green-50 p-4 rounded-lg text-center">
                                                        <p className="text-2xl font-bold text-green-600">
                                                            {Math.round(analysisResult.speech_percentage || 0)}%
                                                        </p>
                                                        <p className="text-sm text-gray-500">Có lời nói</p>
                                                    </div>
                                                    <div className="bg-red-50 p-4 rounded-lg text-center">
                                                        <p className="text-2xl font-bold text-red-600">
                                                            {Math.round(analysisResult.silence_percentage || 0)}%
                                                        </p>
                                                        <p className="text-sm text-gray-500">Im lặng</p>
                                                    </div>
                                                </div>

                                                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm">
                                                    💡 Có thể tiết kiệm khoảng <strong>{Math.round(analysisResult.total_silence_seconds || 0)}s</strong> bằng cách cắt im lặng
                                                </div>
                                            </div>
                                        )}
                                    </>
                                )}

                                {/* Silence Removal Tab */}
                                {activeTab === 'silence' && (
                                    <>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                                    Ngưỡng im lặng (dB): {thresholdDb}
                                                </label>
                                                <input
                                                    type="range"
                                                    min="-50"
                                                    max="-10"
                                                    value={thresholdDb}
                                                    onChange={(e) => setThresholdDb(parseInt(e.target.value))}
                                                    disabled={loading}
                                                    className="w-full"
                                                />
                                                <div className="flex justify-between text-xs text-gray-400 mt-1">
                                                    <span>Nhạy</span>
                                                    <span>Ít nhạy</span>
                                                </div>
                                            </div>

                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                                    Thời gian im lặng tối thiểu: {minSilence}s
                                                </label>
                                                <input
                                                    type="range"
                                                    min="0.1"
                                                    max="2"
                                                    step="0.1"
                                                    value={minSilence}
                                                    onChange={(e) => setMinSilence(parseFloat(e.target.value))}
                                                    disabled={loading}
                                                    className="w-full"
                                                />
                                            </div>
                                        </div>

                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Lề giữ lại xung quanh lời nói: {margin}s
                                            </label>
                                            <input
                                                type="range"
                                                min="0"
                                                max="0.5"
                                                step="0.05"
                                                value={margin}
                                                onChange={(e) => setMargin(parseFloat(e.target.value))}
                                                disabled={loading}
                                                className="w-full"
                                            />
                                        </div>

                                        <div className="p-4 bg-gray-50 rounded-lg">
                                            <label className="flex items-center gap-2 mb-3">
                                                <input
                                                    type="checkbox"
                                                    checked={speedUpSilence !== null}
                                                    onChange={(e) => setSpeedUpSilence(e.target.checked ? 4 : null)}
                                                    disabled={loading}
                                                    className="rounded border-gray-300"
                                                />
                                                <span className="text-sm font-medium">Tăng tốc im lặng thay vì cắt bỏ</span>
                                            </label>
                                            
                                            {speedUpSilence !== null && (
                                                <div>
                                                    <label className="block text-sm text-gray-600 mb-2">
                                                        Tốc độ: {speedUpSilence}x
                                                    </label>
                                                    <input
                                                        type="range"
                                                        min="2"
                                                        max="8"
                                                        value={speedUpSilence}
                                                        onChange={(e) => setSpeedUpSilence(parseInt(e.target.value))}
                                                        disabled={loading}
                                                        className="w-full"
                                                    />
                                                </div>
                                            )}
                                        </div>

                                        <Button
                                            className="w-full bg-green-600 hover:bg-green-700"
                                            onClick={handleRemoveSilence}
                                            disabled={loading}
                                        >
                                            {loading ? '⏳ Đang xử lý...' : '🔇 Cắt Im lặng'}
                                        </Button>
                                    </>
                                )}

                                {/* Smart Trim Tab */}
                                {activeTab === 'trim' && (
                                    <>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                                Thời lượng mục tiêu (giây)
                                            </label>
                                            <Input
                                                type="number"
                                                min={15}
                                                max={300}
                                                value={targetDuration}
                                                onChange={(e) => setTargetDuration(parseInt(e.target.value))}
                                                disabled={loading}
                                            />
                                        </div>

                                        <div className="space-y-3">
                                            <label className="flex items-center gap-2">
                                                <input
                                                    type="checkbox"
                                                    checked={keepStart}
                                                    onChange={(e) => setKeepStart(e.target.checked)}
                                                    disabled={loading}
                                                    className="rounded border-gray-300 text-green-600"
                                                />
                                                <span className="text-sm">Luôn giữ phần mở đầu</span>
                                            </label>
                                            <label className="flex items-center gap-2">
                                                <input
                                                    type="checkbox"
                                                    checked={keepEnd}
                                                    onChange={(e) => setKeepEnd(e.target.checked)}
                                                    disabled={loading}
                                                    className="rounded border-gray-300 text-green-600"
                                                />
                                                <span className="text-sm">Luôn giữ phần kết thúc</span>
                                            </label>
                                        </div>

                                        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
                                            💡 Hệ thống sẽ tự động chọn các đoạn có lời nói quan trọng nhất
                                        </div>

                                        <Button
                                            className="w-full bg-green-600 hover:bg-green-700"
                                            onClick={handleSmartTrim}
                                            disabled={loading}
                                        >
                                            {loading ? '⏳ Đang cắt...' : '⏱️ Cắt Gọn Thông minh'}
                                        </Button>
                                    </>
                                )}

                                {/* Error */}
                                {error && (
                                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                                        {error}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>

                    {/* Result */}
                    <div>
                        <Card>
                            <CardHeader>
                                <CardTitle>Kết quả</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {!result ? (
                                    <div className="text-center py-8 text-gray-400">
                                        <span className="text-4xl">✂️</span>
                                        <p className="mt-2">Video đã chỉnh sửa sẽ hiển thị ở đây</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {result.success ? (
                                            <>
                                                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                                    <p className="text-green-700 font-medium">✅ Xử lý thành công!</p>
                                                </div>

                                                <div className="text-sm space-y-2">
                                                    <p>
                                                        <strong>Trước:</strong> {Math.round(result.original_duration)}s
                                                    </p>
                                                    <p>
                                                        <strong>Sau:</strong> {Math.round(result.new_duration)}s
                                                    </p>
                                                    <p className="text-green-600 font-medium">
                                                        Tiết kiệm: {Math.round(result.time_saved || 0)}s 
                                                        ({Math.round(result.reduction_percentage || 0)}%)
                                                    </p>
                                                </div>

                                                <a
                                                    href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/tools/download/${result.output_path.split('/').pop()}`}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                >
                                                    <Button className="w-full">
                                                        ⬇️ Tải Video
                                                    </Button>
                                                </a>
                                            </>
                                        ) : (
                                            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                                                <p className="text-red-700">{result.error || 'Có lỗi xảy ra'}</p>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    )
}
