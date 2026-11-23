# ADR-005: Principio de Evidencia antes de IA

## Estado
Aceptado

## Contexto
Los Modelos de Lenguaje Grande (LLMs) son propensos a alucinaciones o aproximaciones incorrectas cuando se les pide realizar cálculos numéricos directos, conteos estadísticos o proyecciones financieras sin contexto verificado.

## Decisión
Separar taxativamente la capa de Analítica Determinista de la capa de IA:
1. Todos los cálculos numéricos (sumas, medianas, percentiles, tasas de crecimiento, Opportunity Score, z-scores) se computan exclusivamente mediante código Python determinista y SQL.
2. La IA (Ollama / LLMs externos) actúa únicamente como capa de síntesis, interpretación y estructuración de informes a partir de datos ya calculados y referencias con trazabilidad.
3. Toda recomendación generada por IA debe citar identificadores de evidencia (`evidence_refs`).

## Consecuencias
- La IA nunca realiza inferencias financieras directas sin respaldo computado.
- Se garantiza auditabilidad y reproducibilidad de los informes de mercado.
