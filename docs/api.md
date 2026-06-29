# API Inicial

Swagger local:

```text
http://127.0.0.1:8000/docs
```

## Endpoints principais

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/token`
- `GET /api/v1/users/me`
- `GET /api/v1/companies`
- `GET /api/v1/devices`
- `POST /api/v1/devices`
- `GET /api/v1/dashboards/summary`
- `GET /api/v1/telemetry/devices/{device_id}/latest`
- `GET /api/v1/alerts`
- `GET /api/v1/integrations/thingsboard/status`
- `GET /api/v1/workflows`

## Autenticação

Use JWT Bearer:

```http
Authorization: Bearer <token>
```

O endpoint `/auth/token` existe para compatibilidade com o botão Authorize do Swagger.
