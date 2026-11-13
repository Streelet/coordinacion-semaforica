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
- Visualización armada por adelantado en `visualizacion/` (React Three Fiber): lee un registro por estrategia y lo dibuja; no simula. Por ahora usa datos de demostración de `src/demo_animacion.py`, que no son resultados.
- Formato del registro (contrato Python → página) descrito en `visualizacion/README.md`; el exportador de SimPy deberá producirlo.
- Maqueta comprobada en navegador local el 13 nov: ver integración Kenney abajo.

### Integración Kenney — 2026-11-13
- Incorporados 17 modelos locales: autos, camiones, edificios, árboles, conos y farolas; texturas y licencias CC0 conservadas por paquete. Autobús de la plantilla conservado.
- Comprobado: compilación Vite, 17 GLB servidos y texturas presentes; reproducción/pausa, tiempo y comparación A/B/C en navegador sin errores de consola.
- Evidencia: `resultados/visualizacion/modelos_kenney.png`. Abrir: `http://127.0.0.1:5173/` mientras corre `npm run dev` en `visualizacion/`.
- Alcance: maqueta con registros de demostración; integración con SimPy y validación del modelo pendientes.

### Presentación de la simulación — 2026-11-13
- Regla del usuario: nunca superponer textos ni controles a las simulaciones. Indicadores colocados debajo del canvas, también en comparación A/B/C.
- Fondo blanco, Nunito local y colores azul intenso/neutros fríos; asfalto más oscuro para distinguir calles y vehículos. Cámara elevada centrada en W29–W30.
- Comprobación en navegador: áreas 3D sin texto y los indicadores fuera de sus límites en vista individual y A/B/C; consola sin errores. Compilación correcta. Evidencia: `resultados/visualizacion/interfaz_blanca.png`.

### Ambiente visual — 2026-11-13
- Selector exterior común a A/B/C: sin lluvia, ligera e intensa. Partículas generadas localmente; intensa incorpora relámpagos con pulso de iluminación. Movimiento reducido desactiva destellos; también se omiten a 10× y 30×.
- Ajuste solicitado: lluvia ligera más visible (1,500 gotas, longitud 3.3 m, opacidad 0.70); intensa reforzada (3,200 gotas, longitud 5 m, opacidad 0.80). Tamaños gráficos ilustrativos.
- Alcance: ambiente visual; todavía no cambia demanda, velocidad ni capacidad del modelo. La interfaz lo indica fuera del canvas.
- Revisión inicial en navegador de los tres estados, sin errores de consola. El incremento posterior de visibilidad queda aplicado en código.

### Paneles de paso y llegada del camión — 2026-11-13
- A petición del usuario: dos paneles físicos 3D fuera de la calzada, con indicador de paso normal/reducido según la avería. Excepción específica a la regla de mantener el texto de interfaz fuera del canvas.
- Reducido: máximo 300 veh/h, calculado de 12 s por paso y exportado como metadato; normal: sin restricción adicional (no hay capacidad normal calibrada).
- El camión ahora llega por el lateral libre, frena y se estaciona; al terminar la avería acelera y sale. Conos e indicador reducido sincronizados con el periodo de detención. Esta trayectoria visual no añade llegadas ni modifica las colas ya calculadas.
- Comprobación: llegada visible antes de 1:30, camión estacionado/panel reducido a 2:31 y retirada/panel normal a 6:39; consola sin errores y compilación correcta. Evidencia: `resultados/visualizacion/paneles_paso_camion.png` y `camion_salida.png`.

### Pantalla completa — 2026-11-13
- Cada vista A/B/C puede maximizarse. Controles flotantes en pantalla completa: arrastrables por la cabecera (también con flechas), plegables y limitados a los bordes de la pantalla. Salida por botón o Escape; se conserva el tiempo de reproducción.
- Indicadores compactos a la izquierda: gota con nivel de lluvia y velocímetro de reproducción. Esta velocidad corresponde al reloj de la animación, no a km/h.
- Excepción solicitada a la regla de superposición: controles e indicadores flotantes solo en pantalla completa; en vista normal se mantienen fuera del canvas.
- Comprobados apertura, arrastre, ocultar/mostrar, actualización de indicadores y salida por botón/Escape, sin errores de consola. Compilación correcta. Evidencia: `resultados/visualizacion/pantalla_completa.png`.

### Revisión de preparación para datos — 2026-11-13
- Pendientes propuestos, sin implementar: validar/versionar el contrato de archivos y procedencia; vincular accesos LION y tablas 1:N con rutas; configurar escenario y ejecutar SimPy con entradas comunes a A/B/C; métricas y conservación por todos los accesos; clima desde el calendario de datos; cargar por periodos.
- Precisar métricas actuales: `salidas_tramo` cuenta vehículos que terminan su ruta después de recorrer T, no el cruce de salida de T; el aviso de W30 conserva la primera detección y no identifica episodios activos. La espera fuera de escena se exporta agregada y debe conservar identidad y tiempos por acceso para la evaluación definitiva.
- La lluvia ya afecta λ en la base sintética: no aplicar de nuevo ese factor al importar. Los efectos sobre descarga/velocidad requieren parámetros propios declarados.
- Antes de programar el motor: consolidar la documentación vigente (dos tablas, 19 variables y comparación A→B→C); el borrador aún mezcla esos acuerdos con texto anterior.

### Frontera entre motor y visualización — 2026-11-13
- Contrato JSON v1 compartido en `contratos/`: esquemas, ejemplo y casos inválidos comunes. Exportador Python independiente (`src/exportacion_visual.py`), manifiesto A/B/C y cargador de lectura en la web.
- El cargador valida formato, tiempos, referencias y compatibilidad declarada de red/entradas/réplica/duración. Las métricas usan su vector de tiempos; ya no se presupone muestreo por segundo.
- Corridas existentes migradas sin recalcular tráfico. La demo exporta por defecto a `resultados/demo`; `--salida` permite publicarla en otra carpeta. Colores y radio de giro son opciones gráficas, no requisitos del motor.
- Verificado: 3 pruebas Python y 3 JavaScript, carga de las tres corridas por manifiesto, compilación y navegador sin errores de consola. Evidencia: `resultados/visualizacion/contrato_carga.png`.
- Pendiente: que el futuro motor SimPy registre sus trayectorias y métricas en este contrato; esta capa no valida conservación ni calibración física. Instrucciones breves: `contratos/README.md`.

### Análisis exploratorio (01c) — 2026-11-13
- `01c_analisis_exploratorio.ipynb` reconstruido y ejecutado en el `.venv` (Figuras 21–33): 19 variables sin nulos, relación 1:N íntegra; global no normal, grupo Séptima·laborable·17 h no rechaza normalidad (AD p = 0.24, n = 20).
- Entre llegadas exponencial (media 3.01 s, CV 1.05; P(T>6 s) 0.134 vs 0.136). Lluvia fuerte −12 % (regla −15 %), ligera indistinguible; evento MSG 22:00–23:29 ×1.34; picos en 18:00–19:45.
- Todo valida el generador, no el tráfico real. Siguiente: modelo base de `llegadas` (paso 11).

### Modelo base de llegadas (01d) — 2026-11-13
- Poisson con perfil acceso×hora×tipo_día + lluvia + evento; se excluye `tasa_llegada_vph` (fuga). Separación cronológica inviable con una semana (fin de semana y lluvia fuerte al final): se valida dejando un día completo fuera.
- MAE: referencia 10.0, lineal 10.1, Poisson 9.7; piso de ruido 7.5. Factores recuperados: lluvia fuerte 0.87 (regla 0.85), ligera 0.99 (0.95), evento 1.15. Su μ/0.25 h será la λ de SimPy (paso 12).
