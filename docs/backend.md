# Backend

O backend e uma API FastAPI organizada por modulos de dominio.

## Padrao

```text
router -> service -> repository -> model/database
router -> service -> integration client
```

Regras:

- Routers validam entrada HTTP, permissao e escopo.
- Services orquestram casos de uso e auditoria.
- Repositories concentram queries SQLAlchemy.
- Integracoes externas ficam em `app/infrastructure`.
- ThingsBoard nunca e acessado diretamente pelo frontend.

## Modulos principais

- `auth`
- `users`
- `companies` para Partner, Organization, Site e Asset
- `devices`
- `telemetry`
- `dashboards`
- `alerts`
- `audit`
- `integrations`

IA, WhatsApp, billing, marketplace e mobile permanecem fora da Sprint 2.

## Multi-tenant

Hierarquia:

```text
Partner -> Organization -> Site -> Asset -> Device
```

`Organization` e a fronteira operacional principal. Devices pertencem a uma Organization e a um Asset. Assets pertencem a um Site. Sites pertencem a uma Organization.

## ThingsBoard

Criacao de device:

1. valida RBAC e escopo
2. salva o device localmente em estado `provisioning`
3. cria o device no ThingsBoard
4. grava `thingsboard_device_id`
5. retorna o device sem expor identificadores internos do ThingsBoard

Exclusao de device:

1. valida RBAC e escopo
2. remove o device no ThingsBoard
3. marca o device local como `deleted`

## Qualidade

```bash
python -m pytest
python -m ruff check app tests
python -m mypy app
```
