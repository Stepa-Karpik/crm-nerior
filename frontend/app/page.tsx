'use client'

import { useEffect, useMemo, useState } from 'react'
import { crmApi } from '@/lib/api'
import type { Company, Contact, Deal, Lead, Project, Task, WeeklyBoard, Workspace } from '@/lib/types'
import { Sidebar, type Section } from '@/components/Sidebar'
import { Modal } from '@/components/Modal'
import { CheckCircle2, ChevronRight, Flame, Plus, Search } from '@/components/Icons'

const columnLabels: Record<string, string> = {
  burned: 'Сгоревшие', monday: 'Понедельник', tuesday: 'Вторник', wednesday: 'Среда', thursday: 'Четверг', friday: 'Пятница', saturday: 'Суббота', sunday: 'Воскресенье', future: 'Будущие', backlog: 'Без срока'
}
const visibleColumns = ['burned', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'future', 'backlog']

function fmtDate(value?: string | null) {
  if (!value) return 'без срока'
  return new Intl.DateTimeFormat('ru-RU', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
}

function statusLabel(status: string) {
  return status === 'done' ? 'Готово' : status === 'in_progress' ? 'В работе' : status === 'archived' ? 'Архив' : 'Не начато'
}

function priorityLabel(priority: string) {
  return priority === 'critical' ? 'Критично' : priority === 'high' ? 'Высокий' : priority === 'medium' ? 'Средний' : 'Низкий'
}

export default function AppPage() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark')
  const [lang, setLang] = useState<'RU' | 'EN'>('RU')
  const [section, setSection] = useState<Section>('overview')
  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [workspaceId, setWorkspaceId] = useState<string>('')
  const [projects, setProjects] = useState<Project[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [board, setBoard] = useState<WeeklyBoard | null>(null)
  const [companies, setCompanies] = useState<Company[]>([])
  const [contacts, setContacts] = useState<Contact[]>([])
  const [deals, setDeals] = useState<Deal[]>([])
  const [leads, setLeads] = useState<Lead[]>([])
  const [query, setQuery] = useState('')
  const [modal, setModal] = useState<'task' | 'project' | 'workspace' | null>(null)
  const [newTitle, setNewTitle] = useState('')
  const [newDescription, setNewDescription] = useState('')
  const [newDeadline, setNewDeadline] = useState('')
  const [plannerSettings, setPlannerSettings] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => { document.documentElement.dataset.theme = theme }, [theme])

  async function bootstrap() {
    try {
      setError(null)
      let ws = await crmApi.workspaces()
      if (!ws.length) ws = [await crmApi.createWorkspace('Рабочее пространство')]
      setWorkspaces(ws)
      setWorkspaceId((current) => current || ws[0]?.id || '')
    } catch (e: any) { setError(e.message) }
  }

  async function loadWorkspace(id: string) {
    if (!id) return
    try {
      setError(null)
      const [projectsData, tasksData, boardData, companiesData, contactsData, dealsData, leadsData, settingsData] = await Promise.all([
        crmApi.projects(id), crmApi.tasks(id, query), crmApi.board(id), crmApi.companies(id), crmApi.contacts(id), crmApi.deals(id), crmApi.leads(id), crmApi.plannerSettings()
      ])
      setProjects(projectsData); setTasks(tasksData); setBoard(boardData); setCompanies(companiesData); setContacts(contactsData); setDeals(dealsData); setLeads(leadsData); setPlannerSettings(settingsData)
    } catch (e: any) { setError(e.message) }
  }

  useEffect(() => { bootstrap() }, [])
  useEffect(() => { loadWorkspace(workspaceId) }, [workspaceId])

  const activeWorkspace = workspaces.find((w) => w.id === workspaceId)
  const stats = useMemo(() => ({
    projects: projects.length,
    tasks: tasks.length,
    open: tasks.filter(t => t.status !== 'done').length,
    burned: tasks.filter(t => t.is_burned).length,
    deals: deals.length,
    contacts: contacts.length
  }), [projects, tasks, deals, contacts])

  async function createTask() {
    if (!workspaceId || !newTitle.trim()) return
    await crmApi.createTask(workspaceId, { title: newTitle.trim(), description: newDescription || null, priority: 'medium', status: 'not_started', deadline_at: newDeadline ? new Date(newDeadline).toISOString() : null })
    setModal(null); setNewTitle(''); setNewDescription(''); setNewDeadline('')
    await loadWorkspace(workspaceId)
  }

  async function createProject() {
    if (!workspaceId || !newTitle.trim()) return
    await crmApi.createProject(workspaceId, { name: newTitle.trim(), description: newDescription })
    setModal(null); setNewTitle(''); setNewDescription('')
    await loadWorkspace(workspaceId)
  }

  async function markDone(task: Task) {
    await crmApi.updateTask(workspaceId, task.id, { status: 'done' })
    await loadWorkspace(workspaceId)
  }

  return <div className="app-shell">
    <Sidebar section={section} setSection={setSection} workspaces={workspaces} workspaceId={workspaceId} setWorkspaceId={setWorkspaceId} theme={theme} setTheme={setTheme} lang={lang} setLang={setLang} />
    <main className="main">
      <div className="topbar">
        <div className="crumb"><CheckCircle2 size={18}/><span>{activeWorkspace?.name || 'Nerior CRM'}</span><ChevronRight size={15}/><span>{section}</span></div>
        <div className="actions">
          <button className="btn ghost" onClick={() => window.location.href = process.env.NEXT_PUBLIC_DOCUMENTS_URL || '#'}>Документы</button>
          <button className="btn ghost" onClick={() => window.location.href = process.env.NEXT_PUBLIC_PLANNER_URL || '#'}>Planner</button>
          <button className="btn primary" onClick={() => setModal('task')}><Plus size={17}/>Задача</button>
        </div>
      </div>
      {error && <div className="card pad" style={{borderColor:'var(--danger)', marginBottom:16}}>Ошибка API: {error}</div>}
      {section === 'overview' && <Overview stats={stats} tasks={tasks} setSection={setSection} />}
      {section === 'board' && <Board board={board} onDone={markDone} />}
      {section === 'tasks' && <TasksTable tasks={tasks} query={query} setQuery={setQuery} reload={() => loadWorkspace(workspaceId)} />}
      {section === 'projects' && <Projects projects={projects} onCreate={() => setModal('project')} />}
      {section === 'companies' && <EntityPage title="Компании" items={companies} kind="company" />}
      {section === 'contacts' && <EntityPage title="Контакты" items={contacts} kind="contact" />}
      {section === 'deals' && <EntityPage title="Сделки" items={deals} kind="deal" />}
      {section === 'leads' && <EntityPage title="Лиды" items={leads} kind="lead" />}
      {section === 'documents' && <DocumentsPage workspaceId={workspaceId} projects={projects} />}
      {section === 'settings' && <SettingsPage settings={plannerSettings} refresh={() => loadWorkspace(workspaceId)} />}
      {section === 'admin' && <AdminPage />}
    </main>
    {modal && <Modal title={modal === 'task' ? 'Новая задача' : modal === 'project' ? 'Новый проект' : 'Новое пространство'} onClose={() => setModal(null)}>
      <div className="form-grid">
        <input className="input" placeholder={modal === 'task' ? 'Название задачи' : 'Название проекта'} value={newTitle} onChange={(e) => setNewTitle(e.target.value)} />
        <textarea className="input" placeholder="Описание" rows={4} value={newDescription} onChange={(e) => setNewDescription(e.target.value)} />
        {modal === 'task' && <input className="input" type="datetime-local" value={newDeadline} onChange={(e) => setNewDeadline(e.target.value)} />}
        <div className="actions"><button className="btn" onClick={() => setModal(null)}>Отмена</button><button className="btn primary" onClick={modal === 'task' ? createTask : createProject}>Создать</button></div>
      </div>
    </Modal>}
  </div>
}

function Overview({ stats, tasks, setSection }: { stats: any; tasks: Task[]; setSection: (s: Section) => void }) {
  return <>
    <h1 className="page-title">Рабочий центр</h1><p className="page-subtitle">CRM, задачи, документы и календарь в одном рабочем пространстве.</p>
    <div className="grid cols-4" style={{marginTop:24}}>
      {[['Проекты', stats.projects], ['Задачи', stats.tasks], ['Открытые', stats.open], ['Сгоревшие', stats.burned]].map(([label, value]) => <div className="card pad stat" key={label as string}><div className="stat-label">{label}</div><div className="stat-value">{value as number}</div></div>)}
    </div>
    <div className="split" style={{marginTop:14}}>
      <div className="card pad"><h2>Ближайшие дедлайны</h2>{tasks.slice(0,6).map(t => <div className="entity-item" key={t.id} onClick={() => setSection('board')}><div><b>{t.title}</b><div className="page-subtitle">{fmtDate(t.deadline_at)} · {priorityLabel(t.priority)}</div></div><span className={`pill ${t.status === 'done' ? 'done' : t.is_burned ? 'burned' : 'progress'}`}>{statusLabel(t.status)}</span></div>) || <div className="empty">Нет задач</div>}</div>
      <div className="card pad"><h2>Экосистема</h2><p className="page-subtitle">Задачи автоматически синхронизируются с Planner. Документы открываются в Documents в контексте текущего workspace/project.</p><div className="actions" style={{marginTop:16}}><button className="btn primary" onClick={() => setSection('settings')}>Интеграции</button><button className="btn" onClick={() => setSection('documents')}>Документы</button></div></div>
    </div>
  </>
}

function Board({ board, onDone }: { board: WeeklyBoard | null; onDone: (task: Task) => void }) {
  return <><h1 className="page-title">Недельная доска</h1><p className="page-subtitle">Неделя считается с понедельника 00:00 по Москве. Невыполненное прошлой недели попадает в «Сгоревшие».</p>
    <div className="board" style={{marginTop:22}}>{visibleColumns.map(key => <div className="column" key={key}><div className="column-head"><span>{columnLabels[key]}</span><span>{board?.columns?.[key]?.length || 0}</span></div>{(board?.columns?.[key] || []).map(task => <TaskCard key={task.id} task={task} onDone={onDone} />)}</div>)}</div></>
}

function TaskCard({ task, onDone }: { task: Task; onDone: (task: Task) => void }) {
  return <div className={`task-card ${task.is_burned ? 'burned' : ''}`}><span className="fire" style={{['--stage' as any]: task.fire_stage, ['--fire' as any]: task.fire_color}}/><div className="task-title">{task.title}</div><div className="task-meta"><span className="pill">{priorityLabel(task.priority)}</span><span className={`pill ${task.status === 'done' ? 'done' : task.is_burned ? 'burned' : 'progress'}`}>{statusLabel(task.status)}</span><span>{fmtDate(task.deadline_at)}</span></div>{task.status !== 'done' && <button className="btn" style={{marginTop:10}} onClick={() => onDone(task)}>Готово</button>}</div>
}

function TasksTable({ tasks, query, setQuery, reload }: { tasks: Task[]; query: string; setQuery: (v: string) => void; reload: () => void }) {
  return <><h1 className="page-title">Все задачи</h1><div className="actions" style={{margin:'18px 0'}}><div style={{position:'relative', width:360}}><Search size={16} style={{position:'absolute', left:12, top:12, color:'var(--muted)'}}/><input className="input" style={{paddingLeft:36}} placeholder="Поиск по названию и описанию" value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') reload() }} /></div><button className="btn" onClick={reload}>Найти</button></div><div className="table-wrap"><table><thead><tr><th>Задача</th><th>Статус</th><th>Приоритет</th><th>Дедлайн</th><th>Planner</th></tr></thead><tbody>{tasks.map(t => <tr key={t.id}><td>{t.title}</td><td><span className="pill">{statusLabel(t.status)}</span></td><td>{priorityLabel(t.priority)}</td><td>{fmtDate(t.deadline_at)}</td><td>{t.planner_sync_status}</td></tr>)}</tbody></table></div></>
}

function Projects({ projects, onCreate }: { projects: Project[]; onCreate: () => void }) {
  return <><div className="topbar"><div><h1 className="page-title">Проекты</h1><p className="page-subtitle">Внутри workspace проекты имеют свои календари, документы, участников и канбан.</p></div><button className="btn primary" onClick={onCreate}><Plus size={17}/>Проект</button></div><div className="grid">{projects.map(p => <div className="card pad" key={p.id}><h2>{p.name}</h2><p className="page-subtitle">{p.description || 'Без описания'}</p><div className="actions" style={{marginTop:12}}><span className="pill">{p.status}</span><span className="pill">{p.visibility}</span></div></div>)}</div></>
}

function EntityPage({ title, items, kind }: { title: string; items: any[]; kind: string }) {
  const [selected, setSelected] = useState<any>(items[0])
  useEffect(() => { setSelected(items[0]) }, [items])
  return <><h1 className="page-title">{title}</h1><div className="entity-layout card" style={{marginTop:20}}><div className="entity-list"><div style={{padding:14}}><input className="input" placeholder={`Поиск: ${title.toLowerCase()}`} /></div>{items.map(item => <div className={`entity-item ${selected?.id === item.id ? 'active' : ''}`} key={item.id} onClick={() => setSelected(item)}><div style={{display:'flex', gap:12, alignItems:'center'}}><div className="avatar">{(item.name || item.title || '?').slice(0,2).toUpperCase()}</div><div><b>{item.name || item.title}</b><div className="page-subtitle">{item.email || item.stage || item.legal_name || kind}</div></div></div><ChevronRight size={16}/></div>)}</div><div className="entity-detail">{selected ? <><div className="avatar">{(selected.name || selected.title).slice(0,2).toUpperCase()}</div><h2 style={{fontSize:34, letterSpacing:'-.04em'}}>{selected.name || selected.title}</h2><pre style={{whiteSpace:'pre-wrap', color:'var(--muted)'}}>{JSON.stringify(selected, null, 2)}</pre></> : <div className="empty">Данных пока нет</div>}</div></div></>
}

function DocumentsPage({ workspaceId, projects }: { workspaceId: string; projects: Project[] }) {
  return <><h1 className="page-title">Документы workspace</h1><p className="page-subtitle">Документы загружаются и отображаются строго в выбранном рабочем пространстве. Для проекта можно открыть связанный контекст в Nerior Documents.</p><div className="table-wrap" style={{marginTop:20}}><table><thead><tr><th>Контекст</th><th>Тип</th><th>Действие</th></tr></thead><tbody><tr><td>Workspace {workspaceId.slice(0,8)}</td><td>Общий архив</td><td><button className="btn" onClick={() => window.location.href = `${process.env.NEXT_PUBLIC_DOCUMENTS_URL}/docs?workspace=${workspaceId}`}>Открыть</button></td></tr>{projects.map(p => <tr key={p.id}><td>{p.name}</td><td>Проект</td><td><button className="btn" onClick={() => window.location.href = `${process.env.NEXT_PUBLIC_DOCUMENTS_URL}/docs?workspace=${workspaceId}&project=${p.id}`}>Документы проекта</button></td></tr>)}</tbody></table></div></>
}

function SettingsPage({ settings, refresh }: { settings: any; refresh: () => void }) {
  const [enabled, setEnabled] = useState(true)
  const [notify, setNotify] = useState(true)
  const [hours, setHours] = useState(24)
  useEffect(() => { if (settings) { setEnabled(settings.crm_routes_enabled); setNotify(settings.crm_deadline_notifications_enabled); setHours(settings.crm_deadline_notice_hours) } }, [settings])
  async function save() { await crmApi.updatePlannerSettings({ crm_routes_enabled: enabled, crm_deadline_notifications_enabled: notify, crm_deadline_notice_hours: hours }); refresh() }
  return <><h1 className="page-title">Интеграции</h1><div className="card pad" style={{marginTop:20, maxWidth:860}}><h2>Nerior Planner</h2><div className="form-grid"><label><div className="page-subtitle">Отображать маршруты к CRM задачам</div><div className="actions"><button className={`btn ${enabled ? 'primary' : ''}`} onClick={() => setEnabled(true)}>Отображать</button><button className={`btn ${!enabled ? 'primary' : ''}`} onClick={() => setEnabled(false)}>Не отображать</button></div></label><label><div className="page-subtitle">Уведомления дедлайна</div><div className="actions"><button className={`btn ${notify ? 'primary' : ''}`} onClick={() => setNotify(true)}>Уведомлять</button><button className={`btn ${!notify ? 'primary' : ''}`} onClick={() => setNotify(false)}>Не уведомлять</button></div></label>{notify && <input className="input" type="number" min={1} max={720} value={hours} onChange={(e) => setHours(Number(e.target.value))} placeholder="За сколько часов напоминать" />}<button className="btn primary" onClick={save}>Сохранить</button></div></div></>
}

function AdminPage() {
  return <><h1 className="page-title">Администрирование CRM</h1><p className="page-subtitle">Платформенный админ может найти workspace по владельцу, зайти в проект и проверить права/аудит.</p><div className="card pad" style={{marginTop:20}}><button className="btn primary" onClick={() => window.location.href = process.env.NEXT_PUBLIC_ADMIN_URL || '#'}>Открыть admin.nerior.ru</button></div></>
}
