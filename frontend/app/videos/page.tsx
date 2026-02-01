'use client'

import { useState, useEffect } from 'react'
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/shared'
import { apiClient } from '@/lib/api/client'

interface Video {
    id: string
    title: string
    platform?: string
    file_path: string
    created_at: string
    duration?: number
}

export default function VideosPage() {
    const [url, setUrl] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const [videos, setVideos] = useState<Video[]>([])
    const [loadingVideos, setLoadingVideos] = useState(false)

    // Fetch videos on mount
    useEffect(() => {
        fetchVideos()
    }, [])

    const fetchVideos = async () => {
        setLoadingVideos(true)
        try {
            const response = await apiClient.get('/videos')
            setVideos(response.data.videos || [])
        } catch (err) {
            console.error('Failed to fetch videos:', err)
        } finally {
            setLoadingVideos(false)
        }
    }

    const handleDownload = async () => {
        if (!url.trim()) {
            setError('Please enter a valid URL')
            return
        }

        setLoading(true)
        setError('')
        setSuccess('')

        try {
            const response = await apiClient.post('/videos/download', {
                url: url.trim(),
                platform: 'auto'
            })

            setSuccess(`✅ Video downloaded successfully: ${response.data.title || 'Unknown'}`)
            setUrl('')

            // Refresh video list
            setTimeout(fetchVideos, 1000)
        } catch (err: any) {
            const errorDetail = err.response?.data?.detail || 'Failed to download video'

            // Provide helpful suggestions based on error
            let errorMessage = errorDetail
            if (errorDetail.includes('region-locked') || errorDetail.includes('authentication')) {
                errorMessage += '\n\n💡 Try a different public video (e.g., popular music videos)'
            } else if (errorDetail.includes('unavailable')) {
                errorMessage += '\n\n💡 Check if the video URL is correct and still exists'
            }

            setError(errorMessage)
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (id: string) => {
        if (!confirm('Are you sure you want to delete this video?')) return

        try {
            await apiClient.delete(`/videos/${id}`)
            setSuccess('Video deleted successfully')
            fetchVideos()
        } catch (err) {
            setError('Failed to delete video')
        }
    }

    return (
        <div className="min-h-screen bg-white">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="pb-6 border-b border-gray-200">
                    <h1 className="text-3xl font-bold text-gray-900">Videos</h1>
                    <p className="text-gray-600 mt-1">Download and manage your videos</p>
                </div>

                {/* Download Section */}
                <Card className="mt-8">
                    <CardHeader>
                        <CardTitle>Download Video</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex gap-4">
                            <Input
                                placeholder="Enter video URL (TikTok, YouTube, Instagram...)"
                                value={url}
                                onChange={(e) => setUrl(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleDownload()}
                                className="flex-1"
                                disabled={loading}
                            />
                            <Button
                                onClick={handleDownload}
                                disabled={loading}
                            >
                                {loading ? 'Downloading...' : 'Download'}
                            </Button>
                        </div>
                        <p className="text-sm text-gray-500 mt-2">
                            Supported platforms: TikTok, YouTube, Instagram, Douyin
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                            💡 Tip: Use popular public videos for best results
                        </p>

                        {/* Status Messages */}
                        {error && (
                            <div className="mt-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm whitespace-pre-line">
                                {error}
                            </div>
                        )}
                        {success && (
                            <div className="mt-4 p-3 bg-green-50 border border-green-200 text-green-700 text-sm">
                                {success}
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Video List */}
                <div className="mt-8">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-semibold">Recent Videos</h2>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={fetchVideos}
                            disabled={loadingVideos}
                        >
                            {loadingVideos ? 'Loading...' : 'Refresh'}
                        </Button>
                    </div>

                    {loadingVideos ? (
                        <div className="border border-gray-200 p-8 text-center text-gray-500">
                            Loading videos...
                        </div>
                    ) : videos.length === 0 ? (
                        <div className="border border-gray-200 p-8 text-center text-gray-500">
                            No videos yet. Download your first video above.
                        </div>
                    ) : (
                        <div className="border border-gray-200 divide-y">
                            {videos.map((video) => (
                                <div key={video.id} className="p-4 hover:bg-gray-50 flex justify-between items-center">
                                    <div className="flex-1">
                                        <h3 className="font-medium text-gray-900">{video.title}</h3>
                                        <div className="flex gap-4 mt-1 text-sm text-gray-500">
                                            {video.platform && <span>Platform: {video.platform}</span>}
                                            {video.duration && <span>Duration: {Math.floor(video.duration)}s</span>}
                                            <span>Downloaded: {new Date(video.created_at).toLocaleString()}</span>
                                        </div>
                                        <p className="text-xs text-gray-400 mt-1 font-mono">{video.file_path}</p>
                                    </div>
                                    <div className="flex gap-2 ml-4">
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => handleDelete(video.id)}
                                        >
                                            Delete
                                        </Button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
