# Integração ThingsBoard

O ThingsBoard é um componente interno da plataforma Ultralink Monitor.

## Papel do ThingsBoard

- Receber telemetria via MQTT/HTTP.
- Armazenar séries temporais de dispositivos.
- Controlar credenciais técnicas de dispositivos.
- Fornecer dados ao backend do Ultralink Monitor via REST API.

## Papel do Ultralink Monitor

- Autenticar usuários finais.
- Aplicar regras multiempresa.
- Expor dashboards próprios.
- Centralizar alertas, relatórios e automações.
- Consultar telemetria no ThingsBoard sem expor o provedor.

## Regra de segurança

O frontend nunca deve consumir a API do ThingsBoard. Toda chamada deve passar pelo backend:

```text
Dispositivo -> ThingsBoard -> Backend Ultralink -> Frontend Ultralink
```

Para ações administrativas:

```text
Frontend Ultralink -> Backend Ultralink -> ThingsBoard
```

## Variáveis principais

```text
THINGSBOARD_BASE_URL
THINGSBOARD_USERNAME
THINGSBOARD_PASSWORD
```

Essas variáveis pertencem somente ao backend e não devem ser publicadas no frontend.
