# ADR-009: Expansión PC, Conectores por Capacidades y Mapeo Cross-Platform

## Estado
Aceptado

## Contexto
El ecosistema de PC incluye tiendas y bases de datos complementarias (IGDB, itch.io, GOG, Epic Games Store). De acuerdo con la especificación maestra (Sección 0, 1.2, 3.4-3.7):
- Cada conector debe declarar sus capacidades reales y estado de disponibilidad (`active`, `metadata_only`, `planned`, `unsupported`).
- No deben fusionarse juegos incorrectamente por coincidencia débil de título.
- Nunca deben extraerse datos privados ni utilizarse endpoints internos no autorizados (e.g. launcher de Epic).
- Si un dato no está disponible en una tienda externa, debe registrarse como `unavailable` o `unsupported`, nunca como cero.
- IGDB exige atribución visible de marca.

## Decisión
1. **Conectores y registro de capacidades**:
   - `IGDBConnector`: Requiere Client ID y Client Secret de Twitch Developer Console, genera token OAuth Client Credentials, consulta metadata editorial (géneros, themes, game modes, external_ids) e impone la atribución requerida ("Data provided by IGDB").
   - `ItchConnector`: Utiliza feeds RSS públicos oficiales (`/feed/new.xml`, `/feed/featured.xml`, `/feed/sales.xml`) para descubrimiento público, distinguiendo `public_discovery_data` de `creator_authorized_data`.
   - `GOGConnector`: Opera en modo `metadata_only` sobre fuentes públicas autorizadas; no inventa datos de ventas.
   - `EpicGamesConnector`: Opera en modo `metadata_only` o `unsupported` cuando no hay API pública oficial abierta; respeta términos y no emula tráfico interno.
2. **Mapeo Cross-Platform**: Se implementa `GameCrossReference` con estados de coincidencia explícitos (`verified`, `high_confidence`, `candidate`, `manual`) y métodos documentados (`steam_appid_link`, `title_and_dev`, `manual_match`).

## Consecuencias
- **Positivas**: Integridad de datos preservada; cumplimiento legal y de términos de servicio; extensibilidad transparente a nuevas tiendas.
- **Limitaciones**: Las tiendas secundarias no proporcionan métricas continuas de jugadores en vivo comparables a Steamworks.
