'use client'

import { useCallback } from 'react'
import ReactFlow, {
    Node,
    Edge,
    Controls,
    Background,
    BackgroundVariant,
    useNodesState,
    useEdgesState,
    addEdge,
    Connection,
} from 'reactflow'
import 'reactflow/dist/style.css'

/**
 * Workflow Canvas Component
 * Main workflow editor using ReactFlow
 */

const initialNodes: Node[] = [
    {
        id: '1',
        type: 'default',
        data: { label: 'Video Download' },
        position: { x: 100, y: 100 },
    },
]

const initialEdges: Edge[] = []

export function WorkflowCanvas() {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

    const onConnect = useCallback(
        (params: Connection) => setEdges((eds) => addEdge(params, eds)),
        [setEdges]
    )

    return (
        <div className="h-[600px] border border-gray-200 bg-white">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                fitView
            >
                <Background variant={BackgroundVariant.Dots} gap={12} size={1} color="#e5e7eb" />
                <Controls className="border border-gray-200" />
            </ReactFlow>
        </div>
    )
}
