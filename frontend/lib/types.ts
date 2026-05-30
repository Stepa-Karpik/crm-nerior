export type Workspace = {
  id: string
  owner_user_id: string
  name: string
  description?: string | null
  icon?: string | null
  status: string
}

export type Project = {
  id: string
  workspace_id: string
  name: string
  description?: string | null
  status: string
  visibility: string
  manager_user_id?: string | null
}

export type Task = {
  id: string
  workspace_id: string
  project_id?: string | null
  title: string
  description?: string | null
  priority: 'low' | 'medium' | 'high' | 'critical' | string
  status: 'not_started' | 'in_progress' | 'done' | 'archived' | string
  assignee_user_id?: string | null
  deadline_at?: string | null
  planner_event_id?: string | null
  planner_sync_status: string
  fire_stage: number
  fire_color: string
  day_key: string
  is_burned: boolean
}

export type WeeklyBoard = {
  week_start: string
  week_end: string
  columns: Record<string, Task[]>
}

export type Company = { id: string; name: string; legal_name?: string | null; address?: string | null; website?: string | null }
export type Contact = { id: string; name: string; position?: string | null; email?: string | null; phone?: string | null; company_id?: string | null }
export type Deal = { id: string; title: string; amount?: number | null; currency: string; probability: number; stage: string; deadline_at?: string | null }
export type Lead = { id: string; name: string; phone?: string | null; email?: string | null; source?: string | null; status: string; interest?: string | null }
