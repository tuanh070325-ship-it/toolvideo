'use client'

import { useState } from 'react'
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/shared'

export default function GenerationPage() {
    const [prompt, setPrompt] = useState('')
    const [negativePrompt, setNegativePrompt] = useState('')

    return (
        <div className="min-h-screen bg-white">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="pb-6 border-b border-gray-200">
                    <h1 className="text-3xl font-bold text-gray-900">AI Video Generation</h1>
                    <p className="text-gray-600 mt-1">Generate videos using LTX-Video AI</p>
                </div>

                {/* Generation Form */}
                <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <Card>
                        <CardHeader>
                            <CardTitle>Text to Video</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Prompt</label>
                                    <textarea
                                        className="w-full border border-gray-300 px-4 py-2 h-32 focus:outline-none focus:ring-2 focus:ring-gray-400"
                                        placeholder="Describe the video you want to generate..."
                                        value={prompt}
                                        onChange={(e) => setPrompt(e.target.value)}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Negative Prompt (Optional)</label>
                                    <Input
                                        placeholder="What to avoid in the video..."
                                        value={negativePrompt}
                                        onChange={(e) => setNegativePrompt(e.target.value)}
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Frames</label>
                                        <Input type="number" defaultValue="121" />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Steps</label>
                                        <Input type="number" defaultValue="50" />
                                    </div>
                                </div>

                                <Button className="w-full">Generate Video</Button>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Image to Video</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Upload Image</label>
                                    <div className="border-2 border-dashed border-gray-300 p-8 text-center">
                                        <p className="text-gray-500">Click to upload or drag and drop</p>
                                        <p className="text-sm text-gray-400 mt-1">PNG, JPG up to 10MB</p>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Animation Prompt</label>
                                    <Input placeholder="How should the image animate..." />
                                </div>

                                <Button className="w-full" variant="outline">Generate from Image</Button>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Generation History */}
                <div className="mt-8">
                    <h2 className="text-xl font-semibold mb-4">Generation History</h2>
                    <div className="border border-gray-200">
                        <div className="p-8 text-center text-gray-500">
                            No generations yet. Create your first AI video above.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
