/**
 * TypeScript Types for API Integration
 */

// Workflow Types
export interface Workflow {
    id: string
    name: string
    description: string
    nodes: WorkflowNode[]
    connections: WorkflowConnection[]
    metadata?: {
        category?: string
        tags?: string[]
        [key: string]: any
    }
    created_at?: string
    updated_at?: string
}

export interface WorkflowNode {
    id: string
    type: string
    position?: { x: number; y: number }
    data?: Record<string, any>
}

export interface WorkflowConnection {
    source_node: string
    source_output: string
    target_node: string
    target_input: string
}

// Video Types
export interface Video {
    id: string
    url: string
    title?: string
    platform?: string
    status: 'downloading' | 'processing' | 'completed' | 'failed'
    file_path?: string
    thumbnail?: string
    duration?: number
    created_at: string
    updated_at?: string
}

// Generation Types
export interface GenerationStatus {
    available: boolean
    device: string
    model_loaded: boolean
    message?: string
}

export interface TextToVideoParams {
    prompt: string
    negative_prompt?: string
    num_frames?: number
    height?: number
    width?: number
    num_inference_steps?: number
    guidance_scale?: number
    seed?: number
}

export interface ImageToVideoParams {
    image_path: string
    prompt: string
    num_frames?: number
    num_inference_steps?: number
    guidance_scale?: number
    seed?: number
}

export interface GenerationResult {
    success: boolean
    video_path?: string
    message?: string
    error?: string
}

// API Response Types
export interface ApiResponse<T = any> {
    success: boolean
    data?: T
    message?: string
    error?: string
}

export interface WorkflowListResponse {
    workflows: Workflow[]
    total: number
}

export interface WorkflowExecutionRequest {
    workflow_id: string
    inputs: Record<string, any>
}

export interface WorkflowExecutionResponse {
    success: boolean
    execution_id: string
    outputs?: Record<string, any>
    error?: string
}
