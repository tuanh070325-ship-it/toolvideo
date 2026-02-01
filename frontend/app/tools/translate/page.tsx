'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/shared'
import { apiClient } from '@/lib/api/client'

interface Language {
    code: string
    name: string
}

export default function TranslatePage() {
    const [videoUrl, setVideoUrl] = useState('')
    const [sourceLanguage, setSourceLanguage] = useState('auto')
    const [targetLanguage, setTargetLanguage] = useState('vi')
    const [preserveBgm, setPreserveBgm] = useState(true)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<any>(null)
    const [error, setError] = useState('')
    const [languages, setLanguages] = useState<Language[]>([])

    useEffect(() => {
        fetchLanguages()
    }, [])

    const fetchLanguages = async () => {
        try {
            const response = await apiClient.get('/tools/translate/languages')
            setLanguages(response.data.languages || [])
        } catch (err) {
            console.error('Failed to fetch languages:', err)
            // Fallback
            setLanguages([
                { code: 'vi', name: 'Vietnamese' },
                { code: 'en', name: 'English' },
                { code: 'zh', name: 'Chinese' },
                { code: 'ja', name: 'Japanese' },
                { code: 'ko', name: 'Korean' },
                { code: 'th', name: 'Thai' },
                { code: 'id', name: 'Indonesian' },
            ])
        }
    }

    const handleTranslate = async () => {
        if (!videoUrl.trim()) {
            setError('Vui lòng nhập URL video')
            return
        }

        setLoading(true)
        setError('')
        setResult(null)

        try {
            const response = await apiClient.post('/tools/translate', {
                video_url: videoUrl.trim(),
                source_language: sourceLanguage,
                target_language: targetLanguage,
                preserve_bgm: preserveBgm,
                ai_provider: 'auto'
            })

            setResult(response.data)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Dịch video thất bại')
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
                        <span className="text-4xl">🌐</span>
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">Dịch & Lồng Tiếng Video</h1>
                            <p className="text-gray-500">Nguồn: Pyvideotrans</p>
                        </div>
                    </div>
                    <p className="text-gray-600">
                        Tự động dịch video sang ngôn ngữ khác và lồng tiếng AI tự nhiên.
                        Hỗ trợ giữ lại nhạc nền gốc và nhiều ngôn ngữ khác nhau.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Form */}
                    <div className="lg:col-span-2">
                        <Card>
                            <CardHeader>
                                <CardTitle>Cấu hình Dịch</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                {/* Video URL */}
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
                                    <p className="text-xs text-gray-500 mt-1">
                                        Hỗ trợ: TikTok, YouTube, Instagram, Douyin và nhiều nền tảng khác
                                    </p>
                                </div>

                                {/* Languages */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Ngôn ngữ nguồn
                                        </label>
                                        <select
                                            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            value={sourceLanguage}
                                            onChange={(e) => setSourceLanguage(e.target.value)}
                                            disabled={loading}
                                        >
                                            <option value="auto">🔍 Tự động phát hiện</option>
                                            {languages.map((lang) => (
                                                <option key={lang.code} value={lang.code}>
                                                    {lang.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-2">
                                            Ngôn ngữ đích
                                        </label>
                                        <select
                                            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            value={targetLanguage}
                                            onChange={(e) => setTargetLanguage(e.target.value)}
                                            disabled={loading}
                                        >
                                            {languages.map((lang) => (
                                                <option key={lang.code} value={lang.code}>
                                                    {lang.name}
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                {/* Options */}
                                <div className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        id="preserveBgm"
                                        checked={preserveBgm}
                                        onChange={(e) => setPreserveBgm(e.target.checked)}
                                        disabled={loading}
                                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                    />
                                    <label htmlFor="preserveBgm" className="text-sm text-gray-700">
                                        Giữ lại nhạc nền gốc
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
                                    className="w-full bg-blue-600 hover:bg-blue-700"
                                    onClick={handleTranslate}
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <span className="flex items-center gap-2">
                                            <span className="animate-spin">⏳</span>
                                            Đang dịch video...
                                        </span>
                                    ) : (
                                        '🌐 Dịch & Lồng Tiếng'
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
                                        <span className="text-4xl">🎙️</span>
                                        <p className="mt-2">Video đã dịch sẽ hiển thị ở đây</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {result.success ? (
                                            <>
                                                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                                    <p className="text-green-700 font-medium">✅ Dịch video thành công!</p>
                                                </div>

                                                <div className="text-sm space-y-2">
                                                    <p><strong>Ngôn ngữ nguồn:</strong> {result.source_language}</p>
                                                    <p><strong>Ngôn ngữ đích:</strong> {result.target_language}</p>
                                                    <p><strong>Giọng đọc:</strong> {result.voice_used}</p>
                                                </div>

                                                {result.original_text && (
                                                    <div>
                                                        <p className="font-medium text-sm mb-1">Văn bản gốc:</p>
                                                        <div className="bg-gray-50 p-3 rounded text-xs max-h-24 overflow-auto">
                                                            {result.original_text}
                                                        </div>
                                                    </div>
                                                )}

                                                {result.translated_text && (
                                                    <div>
                                                        <p className="font-medium text-sm mb-1">Văn bản dịch:</p>
                                                        <div className="bg-blue-50 p-3 rounded text-xs max-h-24 overflow-auto">
                                                            {result.translated_text}
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
