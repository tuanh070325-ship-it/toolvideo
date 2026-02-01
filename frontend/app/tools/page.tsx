'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button, Card, CardHeader, CardTitle, CardContent } from '@/components/shared'
import { apiClient } from '@/lib/api/client'

interface Tool {
    id: string
    name: string
    name_en: string
    description: string
    source: string
    endpoints: string[]
}

export default function ToolsPage() {
    const [tools, setTools] = useState<Tool[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        fetchTools()
    }, [])

    const fetchTools = async () => {
        try {
            const response = await apiClient.get('/tools/info')
            setTools(response.data.tools || [])
        } catch (err) {
            console.error('Failed to fetch tools info:', err)
            // Fallback tools data
            setTools([
                {
                    id: 'short-video',
                    name: 'Tạo Video Ngắn Tự Động',
                    name_en: 'Short Video Generator',
                    description: 'Tạo video ngắn hoàn chỉnh từ một từ khóa hoặc chủ đề',
                    source: 'ShortGPT + MoneyPrinterTurbo',
                    endpoints: []
                },
                {
                    id: 'translate',
                    name: 'Dịch & Lồng Tiếng Video',
                    name_en: 'Video Translation & Dubbing',
                    description: 'Dịch video sang ngôn ngữ khác với giọng AI',
                    source: 'Pyvideotrans',
                    endpoints: []
                },
                {
                    id: 'style-transfer',
                    name: 'Chuyển Đổi Phong Cách Video',
                    name_en: 'Video Style Transfer',
                    description: 'Chuyển đổi video sang phong cách anime, hoạt hình, nghệ thuật',
                    source: 'AnimeGANv3',
                    endpoints: []
                },
                {
                    id: 'auto-edit',
                    name: 'Chỉnh Sửa Video Tự Động',
                    name_en: 'Automatic Video Editor',
                    description: 'Tự động cắt im lặng, tăng tốc, cắt gọn video',
                    source: 'Auto-Editor',
                    endpoints: []
                }
            ])
        } finally {
            setLoading(false)
        }
    }

    const getToolIcon = (id: string) => {
        switch (id) {
            case 'short-video':
                return '🎬'
            case 'translate':
                return '🌐'
            case 'style-transfer':
                return '🎨'
            case 'auto-edit':
                return '✂️'
            default:
                return '🔧'
        }
    }

    const getToolColor = (id: string) => {
        switch (id) {
            case 'short-video':
                return 'border-l-4 border-l-purple-500'
            case 'translate':
                return 'border-l-4 border-l-blue-500'
            case 'style-transfer':
                return 'border-l-4 border-l-pink-500'
            case 'auto-edit':
                return 'border-l-4 border-l-green-500'
            default:
                return 'border-l-4 border-l-gray-500'
        }
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="pb-6 border-b border-gray-200 bg-white -mx-4 px-4 mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">
                        🛠️ Công Cụ Video Tích Hợp
                    </h1>
                    <p className="text-gray-600 mt-2">
                        Bộ công cụ xử lý video mạnh mẽ tích hợp từ các dự án mã nguồn mở hàng đầu
                    </p>
                </div>

                {loading ? (
                    <div className="flex justify-center py-12">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {tools.map((tool) => (
                            <Card key={tool.id} className={`hover:shadow-lg transition-shadow ${getToolColor(tool.id)}`}>
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-3">
                                        <span className="text-3xl">{getToolIcon(tool.id)}</span>
                                        <div>
                                            <h3 className="text-xl font-bold text-gray-900">{tool.name}</h3>
                                            <p className="text-sm text-gray-500 font-normal">{tool.name_en}</p>
                                        </div>
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-gray-600 mb-4">{tool.description}</p>
                                    <div className="flex items-center justify-between">
                                        <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                                            Nguồn: {tool.source}
                                        </span>
                                        <Link href={`/tools/${tool.id}`}>
                                            <Button>Sử dụng</Button>
                                        </Link>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}

                {/* Info Section */}
                <div className="mt-12 bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-semibold mb-4">📖 Hướng dẫn sử dụng</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-gray-600">
                        <div>
                            <h3 className="font-medium text-gray-900 mb-2">🎬 Tạo Video Ngắn</h3>
                            <p className="text-sm">
                                Nhập chủ đề bất kỳ, hệ thống sẽ tự động viết kịch bản, 
                                tạo giọng đọc AI, thêm phụ đề và nhạc nền để tạo video hoàn chỉnh.
                            </p>
                        </div>
                        <div>
                            <h3 className="font-medium text-gray-900 mb-2">🌐 Dịch & Lồng Tiếng</h3>
                            <p className="text-sm">
                                Tải video từ bất kỳ nền tảng nào, dịch sang ngôn ngữ mong muốn
                                và tự động lồng tiếng AI với giữ lại nhạc nền.
                            </p>
                        </div>
                        <div>
                            <h3 className="font-medium text-gray-900 mb-2">🎨 Chuyển Đổi Phong Cách</h3>
                            <p className="text-sm">
                                Biến video thành phong cách anime Ghibli, Shinkai, 
                                hoặc các hiệu ứng nghệ thuật khác để tạo nội dung độc đáo.
                            </p>
                        </div>
                        <div>
                            <h3 className="font-medium text-gray-900 mb-2">✂️ Chỉnh Sửa Tự Động</h3>
                            <p className="text-sm">
                                Tự động phát hiện và cắt bỏ đoạn im lặng, tăng tốc phần không có lời,
                                giúp video ngắn gọn và cuốn hút hơn.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
