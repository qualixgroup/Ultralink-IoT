# Ultralink Monitor

Plataforma SaaS para monitoramento IoT corporativo. O produto visível ao usuário final é o Ultralink Monitor; o ThingsBoard fica encapsulado como motor interno de telemetria, integrações e comunicação com dispositivos.

## Estrutura

```text
frontend/  React, Vite, TypeScript, TailwindCSS, React Router, React Query, React Flow
backend/   FastAPI, SQLAlchemy, Alembic, JWT, PostgreSQL, Redis
docs/      Arquitetura, integrações e decisões técnicas
docker/    Infraestrutura local
```

## Subindo localmente

1. Copie os arquivos de ambiente:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
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

Frontend: http://127.0.0.1:5173  
Backend Swagger: http://127.0.0.1:8000/docs  
Backend Health: http://127.0.0.1:8000/health

Usuário inicial de desenvolvimento:

```text
admin@ultralink.io
admin123
```

Em produção, a API bloqueia inicialização com `JWT_SECRET_KEY` fraco, CORS aberto ou senha inicial insegura.

## Regra de integração

Dispositivos, credenciais, telemetria e comandos devem passar pela API do Ultralink Monitor. Nenhuma tela deve expor URL, token, tenant, dashboard ou credencial do ThingsBoard para o usuário final.
