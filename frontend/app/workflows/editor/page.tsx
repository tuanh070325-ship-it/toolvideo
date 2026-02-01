'use client'

import { WorkflowCanvas } from '@/components/workflow/WorkflowCanvas'
import { Button } from '@/components/shared'

export default function WorkflowEditorPage() {
    return (
        <div className="min-h-screen bg-white">
            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex items-center justify-between pb-6 border-b border-gray-200">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Workflow Editor</h1>
                        <p className="text-gray-600 mt-1">Build your video processing workflow</p>
                    </div>
                    <div className="flex gap-2">
                        <Button variant="outline">Save</Button>
                        <Button>Execute</Button>
                    </div>
                </div>

                {/* Workflow Canvas */}
                <div className="mt-8">
                    <WorkflowCanvas />
                </div>

                {/* Node Palette */}
                <div className="mt-8">
                    <h2 className="text-xl font-semibold mb-4">Available Nodes</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        {[
                            'Video Download',
                            'Video Process',
                            'AI Generation',
                            'Add Captions',
                            'Audio Mix',
                            'Export',
                        ].map((node) => (
                            <div
                                key={node}
                                className="p-4 border border-gray-200 text-center cursor-pointer hover:bg-gray-50"
                            >
                                <p className="text-sm font-medium">{node}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}
