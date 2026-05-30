import type { Company, Contact, Deal, Lead, Project, Task, WeeklyBoard, Workspace } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8300/api/v1'
export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message) }
}

async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      'content-type': 'application/json',
      ...(init.headers || {})
    },
    credentials: 'include',
    cache: 'no-store'
  })
  if (!response.ok) {
    let message = response.statusText
    try { message = (await response.json()).error?.message || message } catch {}
    throw new ApiError(response.status, message)
  }
  return response.json()
}

export const crmApi = {
  workspaces: () => api<Workspace[]>('/workspaces'),
  createWorkspace: (name: string) => api<Workspace>('/workspaces', { method: 'POST', body: JSON.stringify({ name }) }),
  projects: (workspaceId: string) => api<Project[]>(`/workspaces/${workspaceId}/projects`),
  createProject: (workspaceId: string, body: { name: string; description?: string }) => api<Project>(`/workspaces/${workspaceId}/projects`, { method: 'POST', body: JSON.stringify(body) }),
  tasks: (workspaceId: string, q = '') => api<Task[]>(`/workspaces/${workspaceId}/tasks${q ? `?q=${encodeURIComponent(q)}` : ''}`),
  board: (workspaceId: string, projectId?: string) => api<WeeklyBoard>(`/workspaces/${workspaceId}/tasks/weekly${projectId ? `?project_id=${projectId}` : ''}`),
  createTask: (workspaceId: string, body: Partial<Task> & { title: string }) => api<Task>(`/workspaces/${workspaceId}/tasks`, { method: 'POST', body: JSON.stringify({ workspace_id: workspaceId, ...body }) }),
  updateTask: (workspaceId: string, taskId: string, body: Partial<Task>) => api<Task>(`/workspaces/${workspaceId}/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify(body) }),
  companies: (workspaceId: string, q = '') => api<Company[]>(`/workspaces/${workspaceId}/crm/companies${q ? `?q=${encodeURIComponent(q)}` : ''}`),
  contacts: (workspaceId: string, q = '') => api<Contact[]>(`/workspaces/${workspaceId}/crm/contacts${q ? `?q=${encodeURIComponent(q)}` : ''}`),
  deals: (workspaceId: string, q = '') => api<Deal[]>(`/workspaces/${workspaceId}/crm/deals${q ? `?q=${encodeURIComponent(q)}` : ''}`),
  leads: (workspaceId: string, q = '') => api<Lead[]>(`/workspaces/${workspaceId}/crm/leads${q ? `?q=${encodeURIComponent(q)}` : ''}`),
  createCompany: (workspaceId: string, name: string) => api<Company>(`/workspaces/${workspaceId}/crm/companies`, { method: 'POST', body: JSON.stringify({ workspace_id: workspaceId, name }) }),
  plannerSettings: () => api<any>('/integrations/planner/settings'),
  updatePlannerSettings: (body: any) => api<any>('/integrations/planner/settings', { method: 'PATCH', body: JSON.stringify(body) })
}
