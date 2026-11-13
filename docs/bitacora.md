# Bitácora

## 2026-11-07
- Objetivo: evaluar contención de la propagación del congestionamiento mediante coordinación semafórica.
- Herramientas: Jupyter para explorar y analizar; SimPy para simular.
- Siguiente: definir corredor, datos disponibles y escenarios comparables.

- Base metodológica: el proyecto se inspira en la aplicación de la metodología de una tesis doctoral; requisitos y referencia en `guias/` (solo local, pendientes de revisión).

- Auditoría 7ym2-wayt: solo 33894 tiene 288 intervalos (22–24 abril 2019); seis tramos objetivo sin registros.
- Decisión: conservar ubicación provisional y buscar aforos complementarios de accesos/giros; notebook e informe guardados.

## 2026-11-08
- Histórico btm5-ppia: ningún registro adicional en W29–W30 o W23; 78 filas diarias en tres referencias cercanas.
- Recomendación: conservar W29–W30 con supuestos sintéticos; se cierra la búsqueda histórica.
- Siguiente: base ficticia propuesta de 2016 filas y 16 variables; generación y SimPy pendientes.

- Aprendizaje: explicar conceptos antes de cada operación; dudas y respuestas en [bitácora de aprendizaje](bitacora_aprendizaje.md).
- Siguiente paso actualizado: comprender la unidad de análisis y cerrar el diccionario antes de generar datos.

- Pregunta de investigación guardada textualmente; ver `presentacion/03_pregunta_investigacion.md`.

## 2026-11-12
- Revisadas las cuatro guías del curso; secuencia, matriz y criterios guardados en [plan de trabajo](plan_trabajo.md).
- Se acordó explicar matemáticas y estadística paso a paso y mantener evidencia y dudas; unidad de análisis y estrategias siguen por definir.
- Siguiente: revisar contexto, fenómeno y objeto; resolver qué representa una fila antes de cerrar variables y generar datos.

- Decisión: comparar tres escenarios en escalera: A fijos independientes → B fijos coordinados por desfase → C = B + regulación por ocupación del tramo.
- La pregunta oficial y el planteamiento se reformularán después para incluir C; mientras tanto se conserva el texto registrado.
- Siguiente: registrar supuestos de modelación y resolver la unidad de análisis (propuesta: tablas 1:N intervalos → vehículos).

- Pregunta reformulada y aprobada: general + tres específicas (A→B, B→C, duración del bloqueo y traslado de colas); la anterior queda como antecedente en `presentacion/03_pregunta_investigacion.md`.
- Siguiente: decidir qué representa cada fila (propuesta 1:N intervalos → vehículos) y cerrar el diccionario.

- Unidad de análisis acordada: tablas 1:N `intervalos` (acceso × 15 min, 2,016 filas) → `vehiculos`; entradas comunes a A, B y C.
- Regla: si un valor depende de la estrategia, es resultado de SimPy, no dato generado.
- Siguiente: diccionario de variables de ambas tablas.

- Diccionario aprobado: 19 variables (13 en `intervalos`, 6 en `vehiculos`), con ordinales `dia_semana` y `lluvia` y factor local `evento_msg`; ver diseño técnico §4.
- Siguiente: reglas de generación (perfiles por hora, factores, proporciones, semillas) antes de generar datos.

## 2026-11-13
- Reglas de generación aprobadas (diseño técnico §5) y base generada con semilla 20261112: 2,016 intervalos y 206,888 vehículos; validaciones de integridad aprobadas.
- Evidencia: `notebooks/01_datos.ipynb` (comentado y ejecutado); datos y manifiesto en `datos/procesados/`. Requisitos de la fase 2 revisados (Figuras 21–33 de la tesis).
- Siguiente: ejecutar el notebook en el `.venv` local, instalar scipy/scikit-learn/bokeh y empezar el análisis exploratorio (fase 2).
