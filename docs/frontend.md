# Frontend

O frontend usa React, Vite, TypeScript, TailwindCSS, React Router e React Query.

## Fluxo Sprint 2

```text
Login -> Organizations -> Sites -> Assets -> Devices -> Device Details
```

Paginas implementadas:

- Dashboard
- Organizations
- Sites
- Assets
- Devices
- Device Details

As telas usam apenas `VITE_API_URL` para falar com o backend. O frontend nao conhece URL, token, tenant, credenciais ou dashboards do ThingsBoard.

## Build

```bash
npm install
npm run build
```

No Docker de producao, o build Vite e servido pelo Nginx na porta interna `80`.

## Dados

React Query e usado para:

- listar entidades
- invalidar listas apos criacao
- atualizar telemetria do Device Details periodicamente

As paginas mantem controles simples de selecao em cascata: Organization, Site, Asset e Device.
