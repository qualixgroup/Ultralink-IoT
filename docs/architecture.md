# Arquitetura

O Ultralink Monitor é organizado como um monorepo com frontend, backend, documentação e infraestrutura local.

## Backend

A API usa FastAPI com separação por módulos de domínio:

- auth
- users
- partners
- organizations
- sites
- assets
- devices
- dashboards
- telemetry
- alerts
- integrations
- ai
- workflows

Cada módulo deve concentrar suas rotas, schemas, regras de aplicação e persistência. A infraestrutura compartilhada fica em `app/infrastructure`, incluindo banco, cache, MQTT e cliente ThingsBoard.

## Clean Architecture

Fluxo recomendado:

```text
router -> service -> repository -> model/database
router -> service -> integration client
```

Regras:

- Rotas não devem conhecer detalhes de provedores externos.
- Services orquestram casos de uso.
- Repositories isolam SQLAlchemy.
- Integrações externas ficam em `app/infrastructure`.
- ThingsBoard nunca é acessado diretamente pelo frontend.

## Frontend

O frontend usa React com Vite, TypeScript, TailwindCSS, React Router e React Query.

Fluxo recomendado:

```text
page -> component -> lib/api -> backend
```

React Flow já está incluído para os fluxos de automação em `workflows`.

## Multiempresa

O modelo SaaS usa a hierarquia:

```text
Partner -> Organization -> Site -> Asset -> Device
```

`Organization` é a fronteira principal de dados do cliente. Usuários, dispositivos, alertas e auditoria carregam `partner_id` e/ou `organization_id` para permitir isolamento por parceiro e organização.

Papéis suportados:

- platform_owner
- platform_admin
- partner_admin
- partner_technician
- organization_admin
- organization_operator
- read_only

Regras principais:

- `platform_owner` acessa tudo.
- `partner_admin` acessa apenas organizações do próprio parceiro.
- `organization_admin` acessa apenas sua organização.
- Telemetria e devices nunca expõem URL, token ou credencial do ThingsBoard.
