# ADR-011: Motor de Exportaciones Multiformato y Capa de Investigación con IA

## Estado
Aceptado

## Contexto
El valor comercial y estratégico de Steam Intelligence reside en generar informes de mercado de alta calidad para la toma de decisiones previas a la producción o lanzamiento (Master Spec Sección 12 y 15). Se requiere:
1. Exportar en 5 formatos clave: **PDF** (ejecutivo/técnico reproducible con ReportLab y texto seleccionable), **PPTX** (presentación 16:9 con temas oscuros editables mediante python-pptx), **XLSX** (hoja de cálculo multilibro con openpyxl), **CSV** y **JSON** (reproducibilidad total).
2. Proporcionar una capa de análisis con IA estructurada que opere sobre **herramientas tipadas y consultas parametrizadas**, sin dar acceso a SQL arbitrario.
3. Proteger la IA contra inyecciones de prompts provenientes de texto de reseñas y no inventar datos de ventas ajenas no publicados.

## Decisión
1. **Pipeline de Exportación**:
   - `ExportService`: Genera documentos nativos con diseño profesional; añade numeración de páginas "Página X de Y", fechas de corte de datos, notas de evidencia y disclaimers metodológicos.
   - Directorio persistente `exports/` accesible mediante descargas seguras con validación de rutas contra directory traversal.
2. **Capa de Investigación con IA**:
   - `AIAnalystService`: Utiliza herramientas tipadas internas (`get_segment_metrics`, `get_niche_opportunities`, `get_review_topics`, `get_release_calendar`) para fundamentar cualquier conclusión en evidencia empírica.
   - Formato estructurado JSON con versionado de prompt (`market-analyst-v1`), bandas de confianza (`high`, `medium`, `low`) y desglose de limitaciones.
   - Capacidad offline/reglas: si no hay LLM externo disponible, sintetiza hallazgos rigurosamente desde la base de datos sin alucinar.

## Consecuencias
- **Positivas**: Informes listos para reuniones de directores o inversores; cumplimiento estricto del principio *evidence-first*; protección total de la integridad de la base de datos.
- **Limitaciones**: La generación de PDFs y PPTX con grandes volúmenes de datos puede requerir algunos segundos de procesamiento.
