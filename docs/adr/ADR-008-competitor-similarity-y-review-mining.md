# ADR-008: Competitor Similarity y Minería de Reseñas sin Sesgo

## Estado
Aceptado

## Contexto
El análisis de competidores y la extracción de opiniones en reseñas (Master Spec Sección 9) requiere:
1. Identificar competidores directos basados en solapamiento de género, tags, mecánicas, precio y fecha de lanzamiento.
2. Extraer quejas y elogios de reseñas públicas con trazabilidad total.
3. Evitar que la IA o los resúmenes afirmen que una queja o elogio es "mayoritario" sin contar la muestra y el denominador real.
4. Prevenir que el texto no confiable de reseñas introduzca inyecciones de instrucciones (*prompt injection*).

## Decisión
1. **Selección de competidores**: Se utiliza el índice Jaccard sobre taxonomías (`game_taxonomies`), bandas de precio y ventanas de lanzamiento para calcular `similarity_score` con razones explícitas (`tag_overlap`, `genre_overlap`, `mechanic_overlap`, `audience_overlap`, `manual_selection`, `semantic_similarity`).
2. **Taxonomía canónica de tópicos**: Se fijan los 15 tópicos maestros descritos en la especificación (bugs/crashes, performance/optimization, controls, ui/ux, difficulty/balance, content/replayability, price/value, multiplayer/network, progression, monetization, accessibility, localization, community/support, positive_gameplay_loop, art/audio/story).
3. **Muestra y Denominador**: Toda conclusión de minería de reseñas debe almacenar y exponer `sample_size`, `complaint_count`, `prevalence_ratio` y citar los IDs exactos de reseña (`source_review_id`).
4. **Sanitización de texto**: Todo texto de reseña procesado es sanitizado contra caracteres de escape de control y directivas de lenguaje para neutralizar inyecciones de prompts antes del análisis.

## Consecuencias
- **Positivas**: Trazabilidad absoluta de afirmaciones (evidence-first); prevención de alucinaciones o exageraciones en los resúmenes comerciales; resistencia a prompt injection.
- **Limitaciones**: La minería de reseñas depende del volumen de reseñas públicas ingeridas por juego.
