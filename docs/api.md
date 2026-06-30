# API

Swagger local:

```text
http://127.0.0.1:8000/docs
```

Todas as rotas de negocio usam JWT Bearer:

```http
Authorization: Bearer <token>
```

## Auth

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/token`
- `GET /api/v1/users/me`

## Partners

- `GET /api/v1/partners`
- `POST /api/v1/partners`
- `GET /api/v1/partners/{partner_id}`
- `PATCH /api/v1/partners/{partner_id}`
- `DELETE /api/v1/partners/{partner_id}`

## Organizations

- `GET /api/v1/organizations`
- `POST /api/v1/organizations`
- `GET /api/v1/organizations/{organization_id}`
- `PATCH /api/v1/organizations/{organization_id}`
- `DELETE /api/v1/organizations/{organization_id}`
- `GET /api/v1/companies` como alias legado de organizations

## Sites

- `GET /api/v1/sites`
- `POST /api/v1/sites`
- `GET /api/v1/sites/{site_id}`
- `PATCH /api/v1/sites/{site_id}`
- `DELETE /api/v1/sites/{site_id}`

## Assets

- `GET /api/v1/assets`
- `POST /api/v1/assets`
- `GET /api/v1/assets/{asset_id}`
- `PATCH /api/v1/assets/{asset_id}`
- `DELETE /api/v1/assets/{asset_id}`

## Devices

- `GET /api/v1/devices`
- `POST /api/v1/devices`
- `GET /api/v1/devices/{device_id}`
- `PATCH /api/v1/devices/{device_id}`
- `DELETE /api/v1/devices/{device_id}`
- `GET /api/v1/devices/{device_id}/telemetry`

`DeviceRead` nunca inclui `thingsboard_device_id`.

## Telemetria

Novo endpoint principal:

```text
GET /api/v1/devices/{device_id}/telemetry
```

Resposta:

```json
{
  "device_id": "...",
  "temperatura": 24.5,
  "bateria": 88.0,
  "combustivel": 62.0,
  "rssi": -67,
  "ultima_atualizacao": "2026-06-30T12:00:00Z",
  "source": "thingsboard"
}
```

Quando nao houver dado fisico, o backend pode retornar telemetria simulada com `source="simulated"`.

Endpoint legado ainda disponivel:

- `GET /api/v1/telemetry/devices/{device_id}/latest`

## Health

- `GET /health`
- `GET /health/full`

`/health/full` valida API, banco, Redis, ThingsBoard e versao Alembic.

## Outros modulos

- `GET /api/v1/dashboards/summary`
- `GET /api/v1/alerts`
- `POST /api/v1/alerts`
- `GET /api/v1/audit`
- `GET /api/v1/integrations/thingsboard/status`
- `GET /api/v1/workflows`
