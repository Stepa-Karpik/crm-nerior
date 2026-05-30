# Nerior CRM

Workspace-based CRM for the Nerior ecosystem.

- `crm.nerior.ru` — CRM frontend
- backend API — workspaces, projects, tasks, kanban, CRM entities, permissions, Planner/Documents links
- shared ecosystem auth and admin integration are implemented through service boundaries described in code and env config

Local development:

```bash
cd backend && python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]' && pytest
cd frontend && npm install && npm run build
```
