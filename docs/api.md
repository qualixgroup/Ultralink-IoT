# API Inicial

Swagger local:

```text
http://127.0.0.1:8000/docs
```

## Endpoints principais

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/token`
- `GET /api/v1/users/me`
- `GET /api/v1/partners`
- `GET /api/v1/organizations`
- `POST /api/v1/organizations`
- `PATCH /api/v1/organizations/{organization_id}`
- `DELETE /api/v1/organizations/{organization_id}`
- `GET /api/v1/companies` como alias legado de organizations
- `GET /api/v1/devices`
- `POST /api/v1/devices`
- `PATCH /api/v1/devices/{device_id}`
- `DELETE /api/v1/devices/{device_id}`
- `GET /api/v1/dashboards/summary`
- `GET /api/v1/telemetry/devices/{device_id}/latest`
- `GET /api/v1/alerts`
- `POST /api/v1/alerts`
- `GET /api/v1/audit`
- `GET /api/v1/integrations/thingsboard/status`
- `GET /api/v1/workflows`

## Autenticação

Use JWT Bearer:

```http
Authorization: Bearer <token>
```

O endpoint `/auth/token` existe para compatibilidade com o botão Authorize do Swagger.

## RBAC

As rotas são protegidas por permissões derivadas dos papéis:

```text
platform_owner
platform_admin
partner_admin
partner_technician
organization_admin
organization_operator
read_only
```

O backend aplica escopo multi-tenant antes de consultar ou criar dados. O frontend nunca deve receber `thingsboard_device_id`, URL, token ou credenciais do ThingsBoard.
