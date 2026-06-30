# ThingsBoard

O ThingsBoard e um componente interno da plataforma Ultralink IoT.

## Papel do ThingsBoard

- Receber telemetria via MQTT/HTTP.
- Armazenar series temporais de dispositivos.
- Controlar credenciais tecnicas de dispositivos.
- Fornecer dados ao backend do Ultralink via REST API.

## Papel do Ultralink IoT

- Autenticar usuarios finais.
- Aplicar RBAC e isolamento multi-tenant.
- Expor dashboards proprios.
- Centralizar inventario, alertas e auditoria.
- Consultar telemetria sem expor o provedor.

## Fluxo

```text
Dispositivo -> ThingsBoard -> Backend Ultralink -> Frontend Ultralink
```

Para operacoes administrativas:

```text
Frontend Ultralink -> Backend Ultralink -> ThingsBoard
```

## Sincronizacao de Device

Ao criar um Device pela API Ultralink:

1. o device e salvo localmente
2. o backend cria o device no ThingsBoard
3. o backend armazena `thingsboard_device_id`
4. o frontend recebe apenas o ID Ultralink

Ao excluir:

1. o backend remove o device no ThingsBoard
2. o device local e marcado como `deleted`

## Seguranca

O frontend nunca deve consumir a API do ThingsBoard. As variaveis abaixo pertencem somente ao backend:

```text
THINGSBOARD_BASE_URL
THINGSBOARD_USERNAME
THINGSBOARD_PASSWORD
```
