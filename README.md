# Ultralink IoT

Plataforma SaaS multi-tenant para monitoramento IoT corporativo. O produto visivel ao usuario final e o Ultralink IoT; o ThingsBoard fica encapsulado como motor interno de telemetria e integracao com dispositivos.

## Sprint 2

Vertical slice funcional:

```text
Login -> Organization -> Site -> Asset -> Device -> Telemetria
```

O frontend usa apenas a API do Ultralink. Nenhuma tela do ThingsBoard, URL interna, token, tenant, dashboard ou credencial e exposta para o usuario final.

## Estrutura

```text
frontend/  React, Vite, TypeScript, TailwindCSS, React Router, React Query
backend/   FastAPI, SQLAlchemy, Alembic, JWT, PostgreSQL, Redis
docs/      API, backend, frontend, RBAC, ThingsBoard e deploy
docker/    Infraestrutura local
```

## Subindo localmente

1. Copie os arquivos de ambiente:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.production.example frontend/.env
```

2. Suba a infraestrutura:

```bash
cd docker
docker compose up -d postgres redis thingsboard
```

3. Rode as migrations:

```bash
cd ../backend
alembic upgrade head
```

4. Inicie a API:

```bash
uvicorn app.main:app --reload
```

5. Inicie o frontend:

```bash
cd ../frontend
npm install
npm run dev
```

## Acessos locais

```text
Frontend: http://127.0.0.1:5173
Backend Swagger: http://127.0.0.1:8000/docs
Backend Health: http://127.0.0.1:8000/health
Backend Full Health: http://127.0.0.1:8000/health/full
```

Usuario inicial de desenvolvimento:

```text
admin@ultralink.io
admin123
```

Em producao, a API bloqueia inicializacao com `JWT_SECRET_KEY` fraco, CORS aberto ou senha inicial insegura.

## Qualidade

```bash
cd backend
python -m pytest
python -m ruff check app tests
python -m mypy app

cd ../frontend
npm run build
```

## Documentacao

- [API](docs/api.md)
- [Backend](docs/backend.md)
- [Frontend](docs/frontend.md)
- [RBAC](docs/rbac.md)
- [ThingsBoard](docs/thingsboard.md)
- [Deploy](docs/deployment.md)
