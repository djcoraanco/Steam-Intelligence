# ADR-007: Conectores por Capacidades y Degradación Elegante

## Estado
Aceptado

## Contexto
Cada plataforma externa (Steamworks, Steam Storefront, SteamSpy, IGDB, itch.io, GOG, Epic Games Store, PCGamingWiki) ofrece diferentes niveles de acceso, tipos de datos, modelos de autenticación y políticas de rate limit. Tratar a todos los proveedores bajo una misma interfaz uniforme rígida causaría errores o forzaría a inventar campos no soportados.

## Decisión
Cada conector declara explícitamente su metadata de registro:
- `provider_code`
- `provider_name`
- `provider_type` (`official_public`, `official_partner`, `third_party_public`, `third_party_restricted`, `user_authorized`)
- `status` (`active`, `planned`, `unavailable`, `deprecated`, `disabled`)
- `capabilities` (lista de capacidades validadas como `catalog`, `metadata`, `prices`, `genres`, `tags`, `screenshots`, `reviews`, `current_players`, `owner_estimates`)
- `authentication` y `rate_limit_policy`

Si un proveedor no soporta un dato o falla temporalmente:
1. El dato se marca como `unsupported` o `unavailable`, nunca se convierte en 0.
2. La interfaz de usuario muestra el estado de degradación elegante (`partial data`, `stale`, `unavailable`).
3. El fallo de un proveedor secundario no interrumpe el resto de los módulos de la plataforma.

## Consecuencias
- Cero alucinación o invención de datos en la plataforma.
- Integración extensible para nuevas fuentes sin alterar la lógica de negocio central.
