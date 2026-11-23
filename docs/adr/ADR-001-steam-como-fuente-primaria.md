# ADR-001: Steam como fuente primaria

## Estado
Aceptado

## Contexto
Steam Intelligence tiene como objetivo proveer inteligencia de mercado para videojuegos de PC. En el ecosistema de PC existen diversas plataformas y tiendas (Steam, Epic Games Store, GOG, itch.io), pero la disponibilidad, profundidad y estandarización de datos públicos varía significativamente entre ellas.

## Decisión
Se establece Steam (Steamworks Web API pública y Storefront API) como la plataforma y fuente primaria de referencia para el MVP y para el diseño del modelo de datos inicial.

## Consecuencias
- **Positivas**: Mayor disponibilidad de catálogo estructurado, jugadores concurrentes (GetNumberOfCurrentPlayers), reseñas públicas con cursor (IUserReviewsService) y taxonomía madura de géneros/tags.
- **Negativas/Limitaciones**: Steam no publica ventas netas, ingresos ni wishlists de terceros; cualquier métrica externa debe marcarse rigurosamente como estimada o derivada.
- **Diseño**: El modelo de datos (`game_platforms`, `platforms`) se diseña multi-plataforma desde el día 1 para admitir Epic, GOG, itch.io e IGDB en fases posteriores sin rotura de esquema.
