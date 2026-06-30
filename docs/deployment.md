# Deploy

Deploy de homologacao recomendado:

| Dominio | Servico |
| --- | --- |
| `api.ultralinkia.site` | FastAPI backend |
| `app.ultralinkia.site` | React frontend via Nginx |
| `monitor.ultralinkia.site` | ThingsBoard administrativo/interno |

Guia detalhado para EasyPanel:

- [EasyPanel](deployment/easypanel.md)

## Backend

Use `backend/.env.production.example` como base.

Porta interna:

```text
8000
```

Antes de liberar a API:

```bash
alembic upgrade head
```

## Frontend

Use `frontend/.env.production.example` como base.

Porta interna:

```text
80
```

`VITE_API_URL` e embutido no build estatico. Ao alterar a URL da API, gere novo build.
