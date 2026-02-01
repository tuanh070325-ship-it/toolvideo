'use client'

import Link from 'next/link'
import { Button, Card, CardHeader, CardTitle, CardContent } from '@/components/shared'

export default function WorkflowsPage() {
    return (
        <div className="min-h-screen bg-white">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex items-center justify-between pb-6 border-b border-gray-200">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Workflows</h1>
                        <p className="text-gray-600 mt-1">Create and manage video processing workflows</p>
                    </div>
                    <Link href="/workflows/editor">
                        <Button>Create Workflow</Button>
                    </Link>
                </div>

                {/* Workflow List */}
                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Download & Process</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-gray-600 mb-4">
                                Download video from URL and apply basic processing
                            </p>
                            <div className="flex gap-2">
                                <Button size="sm" variant="outline">Edit</Button>
                                <Button size="sm" variant="ghost">Delete</Button>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>AI Video Generation</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-sm text-gray-600 mb-4">
                                Generate video using LTX-Video AI from text prompt
                            </p>
                            <div className="flex gap-2">
                                <Button size="sm" variant="outline">Edit</Button>
                                <Button size="sm" variant="ghost">Delete</Button>
                            </div>
                        </CardContent>
                    </Card>

                    <Link href="/workflows/editor">
                        <Card className="border-dashed border-2 flex items-center justify-center cursor-pointer hover:bg-gray-50 h-full">
                            <div className="text-center p-6">
                                <p className="text-gray-400 text-lg mb-2">+</p>
                                <p className="text-sm text-gray-600">Create New Workflow</p>
                            </div>
                        </Card>
                    </Link>
                </div>
            </div>
        </div>
    )
}
