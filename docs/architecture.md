# Arquitetura

O Ultralink Monitor é organizado como um monorepo com frontend, backend, documentação e infraestrutura local.

## Backend

A API usa FastAPI com separação por módulos de domínio:

- auth
- users
- companies
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

O modelo inicial contém `companies` como raiz de escopo. Usuários, dispositivos e alertas carregam `company_id` para permitir isolamento de dados por cliente.
