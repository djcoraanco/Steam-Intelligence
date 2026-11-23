# ADR-010: Inteligencia de Estacionalidad, Cohortes y Detección de Colisión de Lanzamientos

## Estado
Aceptado

## Contexto
El momento de lanzamiento de un videojuego impacta decisivamente su visibilidad inicial (Master Spec Sección 10). Los desarrolladores necesitan entender:
1. Variación estacional de demanda (meses, trimestres, eventos de ofertas).
2. Desempeño por cohortes de lanzamiento (año, mes, Early Access vs Full Release, bandas de precio).
3. Conflictos o colisiones con eventos masivos de la industria (Steam Next Fest, Summer/Autumn/Winter Sales) y acumulaciones de lanzamientos concurrentes en el mismo género.

## Decisión
1. **Modelado de eventos de la industria**: Se crea la entidad `IndustryEvent` con catálogo inicial de eventos conocidos (Steam Next Fest, Sales estacionales de Valve, Black Friday/Navidad) y trazabilidad de fuentes oficiales.
2. **Detector de colisiones**: Analiza una ventana objetivo ($\pm 14$ días o configurable) comparando:
   - Coincidencia con rebajas estacionales o festivales que desvían el tráfico del Storefront.
   - Densidad de competidores del mismo género programados en la misma ventana.
   - Cálculo de score de colisión y recomendación de ventanas alternativas con menor saturación.
3. **Principio metodológico**: Se aplica la regla de oro del Master Spec: *La asociación temporal no debe presentarse como causalidad*. Toda métrica se reporta con tamaño de muestra ($N$) y disclaimer explicativo.

## Consecuencias
- **Positivas**: Orientación táctica con base empírica para la fecha de lanzamiento; mitigación de riesgos de saturación.
- **Limitaciones**: Las fechas de lanzamiento anunciadas por terceros pueden sufrir retrasos imprevistos.
