# Deploy de homologacao no EasyPanel

Este guia prepara a homologacao do Ultralink IoT na VPS Ubuntu com EasyPanel.
O ThingsBoard continua oculto para o usuario final e funciona somente como motor interno de telemetria.

## Dominios

| Dominio | Servico | Porta interna |
| --- | --- | --- |
| `api.ultralinkia.site` | FastAPI backend | `8000` |
| `app.ultralinkia.site` | React frontend via Nginx | `80` |
| `monitor.ultralinkia.site` | ThingsBoard administrativo/interno | porta ja configurada no EasyPanel |

## Ordem de deploy

1. Confirmar que Postgres, Redis e ThingsBoard estao ativos na VPS.
2. Criar ou atualizar o app do backend no EasyPanel.
3. Configurar as variaveis de ambiente do backend.
4. Fazer build/deploy do backend.
5. Rodar `alembic upgrade head` no container/imagem do backend.
6. Reiniciar ou redeployar o backend.
7. Criar ou atualizar o app do frontend.
8. Configurar `VITE_API_URL` no build do frontend.
9. Fazer build/deploy do frontend.
10. Validar `/health`, `/health/full` e login.

## Backend

Crie um app no EasyPanel apontando para o repositorio `qualixgroup/Ultralink-IoT`.

Configuracao sugerida:

| Campo | Valor |
| --- | --- |
| Build context | `backend` |
| Dockerfile | `Dockerfile` dentro do contexto `backend` |
| Porta interna | `8000` |
| Dominio | `api.ultralinkia.site` |
| HTTPS | habilitado |

Use `backend/.env.production.example` como base e configure as variaveis reais no EasyPanel:

```env
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/ultralink_monitor
REDIS_URL=redis://host:6379/0
JWT_SECRET_KEY=uma-chave-forte-com-pelo-menos-32-caracteres
CORS_ORIGINS=https://app.ultralinkia.site
THINGSBOARD_BASE_URL=https://monitor.ultralinkia.site
THINGSBOARD_USERNAME=usuario-do-thingsboard
THINGSBOARD_PASSWORD=senha-do-thingsboard
```

Em `production`, tambem configure `FIRST_SUPERUSER_PASSWORD` com uma senha forte. O valor padrao `admin123` e bloqueado pela configuracao de seguranca.

### Alembic

Antes de liberar a API para uso, rode as migrations no mesmo ambiente do backend:

```bash
alembic upgrade head
```

No EasyPanel, isso pode ser feito pelo console/terminal do app backend depois que a imagem estiver criada, ou como comando temporario do app antes de voltar para o comando padrao do Dockerfile.

Comando padrao do container backend:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips "*"
```

## Frontend

Crie outro app no EasyPanel apontando para o mesmo repositorio.

Configuracao sugerida:

| Campo | Valor |
| --- | --- |
| Build context | `frontend` |
| Dockerfile | `Dockerfile` dentro do contexto `frontend` |
| Porta interna | `80` |
| Dominio | `app.ultralinkia.site` |
| HTTPS | habilitado |

Configure a variavel de build:

```env
VITE_API_URL=https://api.ultralinkia.site/api/v1
```

O frontend e compilado com Vite e servido pelo Nginx. Como `VITE_API_URL` e embutido no build estatico, alteracoes nessa variavel exigem novo build do frontend.

## ThingsBoard

O ThingsBoard deve permanecer acessivel somente pelo dominio administrativo:

```env
THINGSBOARD_BASE_URL=https://monitor.ultralinkia.site
```

Nao exponha URL, token, tenant, dashboard ou credenciais do ThingsBoard no frontend. O usuario final deve acessar apenas `app.ultralinkia.site`, que conversa com `api.ultralinkia.site`.

## Validacao

Depois do deploy:

```bash
curl https://api.ultralinkia.site/health
curl https://api.ultralinkia.site/health/full
```

`/health` deve responder rapido com a API online.
`/health/full` valida API, banco, Redis e ThingsBoard. Se alguma dependencia falhar, ele retorna `503` com o componente em erro.
