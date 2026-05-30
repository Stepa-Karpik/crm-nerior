'use client'

import { Building2, CalendarDays, FolderKanban, Globe2, Home, Languages, LogOut, Moon, Settings, Shield, Sun, Table2, Users, WalletCards } from './Icons'
import type { Workspace } from '@/lib/types'

export type Section = 'overview' | 'board' | 'tasks' | 'projects' | 'companies' | 'contacts' | 'deals' | 'leads' | 'documents' | 'settings' | 'admin'

const nav = [
  ['overview', Home, 'Главная'],
  ['board', FolderKanban, 'Неделя'],
  ['tasks', Table2, 'Все задачи'],
  ['projects', CalendarDays, 'Проекты'],
  ['companies', Building2, 'Компании'],
  ['contacts', Users, 'Контакты'],
  ['deals', WalletCards, 'Сделки'],
  ['leads', Globe2, 'Лиды'],
  ['documents', Table2, 'Документы'],
  ['settings', Settings, 'Интеграции'],
  ['admin', Shield, 'Админ']
] as const

export function Sidebar({ section, setSection, workspaces, workspaceId, setWorkspaceId, theme, setTheme, lang, setLang }: {
  section: Section
  setSection: (section: Section) => void
  workspaces: Workspace[]
  workspaceId?: string
  setWorkspaceId: (id: string) => void
  theme: 'dark' | 'light'
  setTheme: (theme: 'dark' | 'light') => void
  lang: 'RU' | 'EN'
  setLang: (lang: 'RU' | 'EN') => void
}) {
  return <aside className="sidebar">
    <div className="brand">
      <div className="brand-mark">N</div>
      <div><div className="brand-title">Nerior CRM</div><div className="brand-sub">workspace system</div></div>
    </div>
    <div className="workspace-select">
      <select value={workspaceId || ''} onChange={(e) => setWorkspaceId(e.target.value)}>
        {workspaces.map((w) => <option value={w.id} key={w.id}>{w.name}</option>)}
      </select>
    </div>
    <nav className="nav">
      <div className="nav-label">Навигация</div>
      {nav.map(([key, Icon, label]) => <button key={key} className={`nav-btn ${section === key ? 'active' : ''}`} onClick={() => setSection(key)}><Icon />{label}</button>)}
    </nav>
    <div className="sidebar-bottom">
      <button className="nav-btn" onClick={() => setLang(lang === 'RU' ? 'EN' : 'RU')}><Languages />{lang}</button>
      <button className="nav-btn" onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}>{theme === 'dark' ? <Sun /> : <Moon />}{theme === 'dark' ? 'Светлая тема' : 'Тёмная тема'}</button>
      <button className="nav-btn"><Users />karpik</button>
      <button className="nav-btn"><LogOut />Выйти</button>
    </div>
  </aside>
}
