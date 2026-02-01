import Link from 'next/link'
import { Button, Card, CardHeader, CardTitle, CardContent } from '@/components/shared'

export default function HomePage() {
    return (
        <div className="min-h-screen bg-white">
            <div className="max-w-7xl mx-auto px-4 py-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">
                    Dashboard
                </h1>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Videos Processed</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-4xl font-bold">0</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Workflows</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-4xl font-bold">0</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>AI Generations</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-4xl font-bold">0</p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Tools Used</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-4xl font-bold">0</p>
                        </CardContent>
                    </Card>
                </div>

                {/* Integrated Tools Section */}
                <div className="mt-8 border-t border-gray-200 pt-8">
                    <h2 className="text-xl font-semibold mb-4">🛠️ Công Cụ Tích Hợp</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <Link href="/tools/short-video">
                            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-purple-500 h-full">
                                <CardContent className="pt-4">
                                    <div className="flex items-center gap-3 mb-2">
                                        <span className="text-2xl">🎬</span>
                                        <h3 className="font-semibold">Tạo Video Ngắn</h3>
                                    </div>
                                    <p className="text-sm text-gray-500">Tự động tạo video từ chủ đề</p>
                                </CardContent>
                            </Card>
                        </Link>

                        <Link href="/tools/translate">
                            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-blue-500 h-full">
                                <CardContent className="pt-4">
                                    <div className="flex items-center gap-3 mb-2">
                                        <span className="text-2xl">🌐</span>
                                        <h3 className="font-semibold">Dịch & Lồng Tiếng</h3>
                                    </div>
                                    <p className="text-sm text-gray-500">Dịch video sang ngôn ngữ khác</p>
                                </CardContent>
                            </Card>
                        </Link>

                        <Link href="/tools/style-transfer">
                            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-pink-500 h-full">
                                <CardContent className="pt-4">
                                    <div className="flex items-center gap-3 mb-2">
                                        <span className="text-2xl">🎨</span>
                                        <h3 className="font-semibold">Phong Cách Anime</h3>
                                    </div>
                                    <p className="text-sm text-gray-500">Chuyển video sang anime/2D</p>
                                </CardContent>
                            </Card>
                        </Link>

                        <Link href="/tools/auto-edit">
                            <Card className="hover:shadow-lg transition-shadow border-l-4 border-l-green-500 h-full">
                                <CardContent className="pt-4">
                                    <div className="flex items-center gap-3 mb-2">
                                        <span className="text-2xl">✂️</span>
                                        <h3 className="font-semibold">Cắt Tự Động</h3>
                                    </div>
                                    <p className="text-sm text-gray-500">Cắt im lặng, cắt gọn thông minh</p>
                                </CardContent>
                            </Card>
                        </Link>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="mt-8 border-t border-gray-200 pt-8">
                    <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        <Link href="/tools">
                            <Button className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700">
                                🛠️ Tất Cả Công Cụ
                            </Button>
                        </Link>
                        <Link href="/workflows/editor">
                            <Button variant="outline" className="w-full">Create Workflow</Button>
                        </Link>
                        <Link href="/videos">
                            <Button variant="outline" className="w-full">Download Video</Button>
                        </Link>
                        <Link href="/generation">
                            <Button variant="ghost" className="w-full">AI Generation</Button>
                        </Link>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="mt-8 border-t border-gray-200 pt-8">
                    <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
                    <div className="border border-gray-200 p-8 text-center text-gray-500">
                        No recent activity
                    </div>
                </div>
            </div>
        </div>
    )
}
