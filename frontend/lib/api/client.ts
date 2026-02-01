import axios from 'axios'
import type {
    Workflow,
    WorkflowListResponse,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    Video,
    GenerationStatus,
    TextToVideoParams,
    ImageToVideoParams,
    GenerationResult,
} from '@/lib/types/api'

/**
 * API Client for Backend Communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Health Check
export const healthAPI = {
    check: () => api.get('/health'),
}

// Video APIs
export const videoAPI = {
    list: () => api.get<{ videos: Video[] }>('/videos'),
    get: (id: string) => api.get<Video>(`/videos/${id}`),
    download: (url: string, platform?: string) =>
        api.post<Video>('/videos/download', { url, platform }),
    delete: (id: string) => api.delete(`/videos/${id}`),
}

// Workflow APIs
export const workflowAPI = {
    list: () => api.get<WorkflowListResponse>('/workflows/list'),

    get: (id: string) => api.get<Workflow>(`/workflows/${id}`),

    create: (workflow: Omit<Workflow, 'id' | 'created_at' | 'updated_at'>) =>
        api.post<{ workflow_id: string }>('/workflows/create', workflow),

    update: (id: string, workflow: Partial<Workflow>) =>
        api.put<{ success: boolean }>(`/workflows/${id}`, workflow),

    delete: (id: string) => api.delete<{ success: boolean }>(`/workflows/${id}`),

    execute: (request: WorkflowExecutionRequest) =>
        api.post<WorkflowExecutionResponse>('/workflows/execute', request),

    templates: () => api.get<WorkflowListResponse>('/workflows/templates'),
}

// Generation APIs
export const generationAPI = {
    status: () => api.get<GenerationStatus>('/generation/status'),

    textToVideo: (params: TextToVideoParams) =>
        api.post<GenerationResult>('/generation/text-to-video', params),

    imageToVideo: (params: ImageToVideoParams) =>
        api.post<GenerationResult>('/generation/image-to-video', params),
}

// Export as both default and named export for compatibility
export const apiClient = api
export default api
