'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/shared'
import { apiClient } from '@/lib/api/client'

interface Style {
    id: string
    name: string
    description: string
    type: string
}

export default function StyleTransferPage() {
    const [videoUrl, setVideoUrl] = useState('')
    const [selectedStyle, setSelectedStyle] = useState('anime_hayao')
    const [intensity, setIntensity] = useState(1.0)
    const [preserveAudio, setPreserveAudio] = useState(true)
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<any>(null)
    const [error, setError] = useState('')
    const [styles, setStyles] = useState<Style[]>([])

    useEffect(() => {
        fetchStyles()
    }, [])

    const fetchStyles = async () => {
        try {
            const response = await apiClient.get('/tools/style-transfer/styles')
            setStyles(response.data.styles || [])
        } catch (err) {
            console.error('Failed to fetch styles:', err)
            // Fallback
            setStyles([
                { id: 'anime_hayao', name: 'Hayao Miyazaki Style', description: 'Ghibli-inspired anime', type: 'anime' },
                { id: 'anime_shinkai', name: 'Makoto Shinkai Style', description: 'Your Name style', type: 'anime' },
                { id: 'cartoon', name: 'Cartoon Style', description: 'Classic cartoon look', type: 'cartoon' },
                { id: 'pencil_sketch', name: 'Pencil Sketch', description: 'Black and white sketch', type: 'artistic' },
                { id: 'watercolor', name: 'Watercolor', description: 'Watercolor painting', type: 'artistic' },
                { id: 'vintage', name: 'Vintage Film', description: 'Retro film effect', type: 'filter' },
                { id: 'cyberpunk', name: 'Cyberpunk', description: 'Neon cyberpunk aesthetic', type: 'filter' },
            ])
        }
    }

    const handleApply = async () => {
        if (!videoUrl.trim()) {
            setError('Vui lòng nhập URL video')
            return
        }

        setLoading(true)
        setError('')
        setResult(null)

        try {
            const response = await apiClient.post('/tools/style-transfer', {
                video_url: videoUrl.trim(),
                style: selectedStyle,
                intensity,
                preserve_audio: preserveAudio
            })

            setResult(response.data)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Chuyển đổi phong cách thất bại')
        } finally {
            setLoading(false)
        }
    }

    const getStyleTypeColor = (type: string) => {
        switch (type) {
            case 'anime': return 'bg-pink-100 text-pink-700'
            case 'cartoon': return 'bg-orange-100 text-orange-700'
            case 'artistic': return 'bg-purple-100 text-purple-700'
            case 'filter': return 'bg-blue-100 text-blue-700'
            default: return 'bg-gray-100 text-gray-700'
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
                        <span className="text-4xl">🎨</span>
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">Chuyển Đổi Phong Cách Video</h1>
                            <p className="text-gray-500">Nguồn: AnimeGANv3</p>
                        </div>
                    </div>
                    <p className="text-gray-600">
                        Biến video thành phong cách anime Ghibli, Shinkai, hoạt hình, 
                        hoặc các hiệu ứng nghệ thuật khác để tạo nội dung độc đáo và tránh bản quyền.
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Form */}
                    <div className="lg:col-span-2">
                        <Card>
                            <CardHeader>
                                <CardTitle>Cấu hình Chuyển Đổi</CardTitle>
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
                                </div>

                                {/* Style Selection */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-3">
                                        Chọn phong cách
                                    </label>
                                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                        {styles.map((style) => (
                                            <button
                                                key={style.id}
                                                onClick={() => setSelectedStyle(style.id)}
                                                disabled={loading}
                                                className={`p-3 rounded-lg border-2 text-left transition-all ${
                                                    selectedStyle === style.id
                                                        ? 'border-pink-500 bg-pink-50'
                                                        : 'border-gray-200 hover:border-gray-300'
                                                }`}
                                            >
                                                <div className="flex items-center justify-between mb-1">
                                                    <span className="font-medium text-sm">{style.name}</span>
                                                    {selectedStyle === style.id && (
                                                        <span className="text-pink-500">✓</span>
                                                    )}
                                                </div>
                                                <p className="text-xs text-gray-500">{style.description}</p>
                                                <span className={`text-xs px-2 py-0.5 rounded mt-2 inline-block ${getStyleTypeColor(style.type)}`}>
                                                    {style.type}
                                                </span>
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Intensity */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Cường độ hiệu ứng: {Math.round(intensity * 100)}%
                                    </label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="1"
                                        step="0.1"
                                        value={intensity}
                                        onChange={(e) => setIntensity(parseFloat(e.target.value))}
                                        disabled={loading}
                                        className="w-full"
                                    />
                                    <div className="flex justify-between text-xs text-gray-400 mt-1">
                                        <span>Nhẹ</span>
                                        <span>Mạnh</span>
                                    </div>
                                </div>

                                {/* Options */}
                                <div className="flex items-center gap-2">
                                    <input
                                        type="checkbox"
                                        id="preserveAudio"
                                        checked={preserveAudio}
                                        onChange={(e) => setPreserveAudio(e.target.checked)}
                                        disabled={loading}
                                        className="rounded border-gray-300 text-pink-600 focus:ring-pink-500"
                                    />
                                    <label htmlFor="preserveAudio" className="text-sm text-gray-700">
                                        Giữ lại âm thanh gốc
                                    </label>
                                </div>

                                {/* Warning */}
                                <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-700">
                                    ⚠️ Chuyển đổi phong cách có thể mất vài phút tùy thuộc vào độ dài video.
                                </div>

                                {/* Error */}
                                {error && (
                                    <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                                        {error}
                                    </div>
                                )}

                                {/* Submit */}
                                <Button
                                    className="w-full bg-pink-600 hover:bg-pink-700"
                                    onClick={handleApply}
                                    disabled={loading}
                                >
                                    {loading ? (
                                        <span className="flex items-center gap-2">
                                            <span className="animate-spin">⏳</span>
                                            Đang chuyển đổi...
                                        </span>
                                    ) : (
                                        '🎨 Áp dụng Phong cách'
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
                                        <span className="text-4xl">🖼️</span>
                                        <p className="mt-2">Video đã chuyển đổi sẽ hiển thị ở đây</p>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {result.success ? (
                                            <>
                                                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                                                    <p className="text-green-700 font-medium">✅ Chuyển đổi thành công!</p>
                                                </div>

                                                <div className="text-sm space-y-2">
                                                    <p><strong>Phong cách:</strong> {result.style_name}</p>
                                                    <p><strong>Cường độ:</strong> {Math.round(result.intensity * 100)}%</p>
                                                    <p><strong>Số khung hình:</strong> {result.frame_count}</p>
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
