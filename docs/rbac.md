# RBAC

O backend combina permissao por papel com escopo multi-tenant.

## Papeis

| Papel | Escopo |
| --- | --- |
| `platform_owner` | tudo |
| `platform_admin` | tudo, exceto restricoes de ownership futuras |
| `partner_admin` | somente o proprio Partner |
| `partner_technician` | operacao tecnica dentro do Partner |
| `organization_admin` | somente a propria Organization |
| `organization_operator` | leitura e operacao controlada dentro da Organization |
| `read_only` | apenas leitura |

## Regras

- `platform_owner` enxerga tudo.
- `partner_admin` nao acessa dados de outro Partner.
- `organization_admin` nao acessa dados de outra Organization.
- `read_only` nao cria, edita nem exclui.
- Todos os endpoints de CRUD exigem permissao explicita.
- Endpoints por ID validam tambem o escopo do recurso.

## Dependencias

Principais dependencias em `app/common/dependencies.py`:

- `require_role`
- `require_permission`
- `require_partner_access`
- `require_organization_access`
- `require_asset_access`
- `require_device_access`

## Permissoes

Permissoes ficam em `app/core/rbac.py`, por exemplo:

- `partners:read`
- `partners:write`
- `organizations:read`
- `organizations:write`
- `sites:read`
- `sites:write`
- `assets:read`
- `assets:write`
- `devices:read`
- `devices:write`
- `telemetry:read`
