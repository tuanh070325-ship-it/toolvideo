'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/shared'
import { apiClient } from '@/lib/api/client'

interface Style {
    id: string
    name: string
    description: string
    bgm_style: string
}

interface Platform {
    id: string
    name: string
    width: number
    height: number
    max_duration: number
}

export default function ShortVideoPage() {
    const [topic, setTopic] = useState('')
    const [platform, setPlatform] = useState('tiktok')
    const [style, setStyle] = useState('storytelling')
    const [duration, setDuration] = useState(60)
    const [language, setLanguage] = useState('vi')
    const [addCaptions, setAddCaptions] = useState(true)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<any>(null)
    const [error, setError] = useState('')
    const [styles, setStyles] = useState<Style[]>([])
    const [platforms, setPlatforms] = useState<Platform[]>([])

    useEffect(() => {
        fetchOptions()
    }, [])

    const fetchOptions = async () => {
        try {
            const response = await apiClient.get('/tools/short-video/styles')
            setStyles(response.data.styles || [])
            setPlatforms(response.data.platforms || [])
        } catch (err) {
            console.error('Failed to fetch options:', err)
            // Fallback
            setStyles([
                { id: 'storytelling', name: 'Story Narration', description: 'Engaging narrative', bgm_style: 'cinematic' },
                { id: 'educational', name: 'Educational', description: 'Informative content', bgm_style: 'upbeat' },
                { id: 'news', name: 'News/Facts', description: 'Quick news', bgm_style: 'news' },
                { id: 'motivation', name: 'Motivational', description: 'Inspiring messages', bgm_style: 'inspiring' },
                { id: 'entertainment', name: 'Entertainment', description: 'Fun content', bgm_style: 'cheerful' },
            ])
            setPlatforms([
                { id: 'tiktok', name: 'TikTok', width: 1080, height: 1920, max_duration: 180 },
                { id: 'reels', name: 'Reels', width: 1080, height: 1920, max_duration: 90 },
                { id: 'shorts', name: 'Shorts', width: 1080, height: 1920, max_duration: 60 },
            ])
        }
    }

    const handleGenerate = async () => {
        if (!topic.trim()) {
            setError('Vui lòng nhập chủ đề')
            return
        }

        setLoading(true)
        setError('')
        setResult(null)

        try {
            const response = await apiClient.post('/tools/short-video/generate', {
                topic: topic.trim(),
                platform,
                style,
                duration,
                language,
                add_captions: addCaptions,
                ai_provider: 'auto'
            })

            setResult(response.data)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Tạo video thất bại')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-5xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex items-center gap-4 mb-8">
                    <Link href="/tools" className="text-gray-500 hover:text-gray-700">
                        ← Quay lại
                    </Link>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
                    <div className="flex items-center gap-3 mb-4">
                        <span className="text-4xl">🎬</span>
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">Tạo Video Ngắn Tự Động</h1>
                            <p className="text-gray-500">Nguồn: ShortGPT + MoneyPrinterTurbo</p>
                        </div>
                    </div>
                    <p className="text-gray-600">
                        Chỉ cần nhập chủ đề, hệ thống sẽ tự động tạo kịch bản, giọng đọc AI, 
                        thêm phụ đề và nhạc nền để tạo video hoàn chỉnh cho TikTok, Reels, Shorts.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Form */}
                    <div className="lg:col-span-2">
                        <Card>
                            <CardHeader>
                                <CardTitle>Cấu hình Video</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                {/* Topic */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Chủ đề / Từ khóa *
                                    </label>
                                    <textarea
                                        className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                                        placeholder="Ví dụ: 5 sự thật thú vị về vũ trụ, Cách tiết kiệm tiền hiệu quả, Câu chuyện kinh dị lúc nửa đêm..."
                                        rows={3}
                                        value={topic}
                                        onChange={(e) => setTopic(e.target.value)}
                                        disabled={loading}
                                    />
                                </div>

                                {/* Platform & Style */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Nền tảng
                                        </label>
                                        <select
                                            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                            value={platform}
                                            onChange={(e) => setPlatform(e.target.value)}
                                            disabled={loading}
                                        >
                                            {platforms.map((p) => (
                                                <option key={p.id} value={p.id}>
                                                    {p.name} ({p.max_duration}s max)
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Phong cách
                                        </label>
                                        <select
                                            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                            value={style}
                                            onChange={(e) => setStyle(e.target.value)}
                                            disabled={loading}
                                        >
                                            {styles.map((s) => (
                                                <option key={s.id} value={s.id}>
                                                    {s.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                {/* Duration & Language */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Thời lượng (giây)
                                        </label>
                                        <Input
                                            type="number"
                                            min={15}
                                            max={180}
                                            value={duration}
                                            onChange={(e) => setDuration(parseInt(e.target.value))}
                                            disabled={loading}
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Ngôn ngữ
                                        </label>
                                        <select
                                            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500"
                                            value={language}
                                            onChange={(e) => setLanguage(e.target.value)}
                                            disabled={loading}
                                        >
                                            <option value="vi">Tiếng Việt</option>
                                            <option value="en">English</option>
                                        </select>
                                    </div>
                                </div>

                                {/* Options */}
                                <div className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        id="captions"
                                        checked={addCaptions}
                                        onChange={(e) => setAddCaptions(e.target.checked)}
                                        disabled={loading}
                                        className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                                    />
                                    <label htmlFor="captions" className="text-sm text-gray-700">
                                        Thêm phụ đề tự động
                                    </label>
                                </div>

                                {/* Error */}
                                {error && (
                                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                                        {error}
                                    </div>
                                )}

                                {/* Submit */}
                                <Button
                                    className="w-full bg-purple-600 hover:bg-purple-700"
                                    onClick={handleGenerate}
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <span className="flex items-center gap-2">
                                            <span className="animate-spin">⏳</span>
                                            Đang tạo video...
                                        </span>
                                    ) : (
                                        '🎬 Tạo Video'
                                    )}
                                </Button>
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
                                        <span className="text-4xl">📹</span>
                                        <p className="mt-2">Video sẽ hiển thị ở đây</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {result.success ? (
                                            <>
                                                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                                    <p className="text-green-700 font-medium">✅ Tạo video thành công!</p>
                                                </div>

                                                <div className="text-sm space-y-2">
                                                    <p><strong>Chủ đề:</strong> {result.topic}</p>
                                                    <p><strong>Thời lượng:</strong> {Math.round(result.duration)}s</p>
                                                    <p><strong>Nền tảng:</strong> {result.platform}</p>
                                                </div>

                                                {result.script && (
                                                    <div>
                                                        <p className="font-medium text-sm mb-1">Kịch bản:</p>
                                                        <div className="bg-gray-50 p-3 rounded text-xs max-h-40 overflow-auto">
                                                            {result.script}
                                                        </div>
                                                    </div>
                                                )}

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
