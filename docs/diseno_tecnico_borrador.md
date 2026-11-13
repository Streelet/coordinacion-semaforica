# Diseño técnico del experimento — borrador para revisión

**Estado:** propuesta didáctica; todavía no aprobada. No se generó la base y no se implementó SimPy.

## 1. Qué representa una fila

**Decisión (12 nov 2026), sustituye la propuesta de esta sección donde la contradiga:** la base ficticia tendrá dos tablas relacionadas 1:N. `intervalos`: una fila por acceso externo e intervalo de 15 minutos (7 × 96 × 3 = 2,016 filas). `vehiculos`: una fila por vehículo, con `intervalo_id` y su instante de llegada; el conteo de cada intervalo debe coincidir con sus vehículos. Ambas tablas son entradas comunes a A, B y C: la estrategia, la réplica y los parámetros semafóricos van en la configuración de escenarios, no en estas filas. Esperas, colas y salidas son resultados de SimPy y se guardan aparte por estrategia.

La fila de la tabla principal representa **un acceso externo, en un intervalo de 15 minutos, bajo una estrategia y una réplica**. Los accesos de entrada que tenemos identificados son:

| Acceso | Entrada a la red | Sentido | Tratamiento de la demanda |
|---|---|---|---|
| 33804 | Seventh Avenue desde W31 hacia W30 | sur (SB) | sintética |
| 33803 | W30 desde Eighth Avenue hacia Seventh | este (EB) | sintética |
| 33894 | W29 desde Sixth Avenue hacia Seventh | oeste (WB) | perfil sintético informado parcialmente por conteos históricos de 2019 |

El segmento interno 33802 conecta W30 con W29 hacia el sur. No es un cuarto acceso externo: sus vehículos son los que pasan por la red y su ocupación/cola se calcula dentro de la simulación. Los segmentos de salida tampoco son demanda de llegada.

Con siete días, 96 intervalos diarios y tres accesos hay `7 × 96 × 3 = 2,016` filas por estrategia y réplica. Para comparar dos estrategias con `R` réplicas pareadas: `2 × R × 2,016` filas. La fila de llegada de 15 minutos no es un vehículo individual ni una observación histórica: el conteo sintético se convertirá en eventos individuales al ejecutar el modelo.

### Conteos agregados a llegadas individuales

Si el perfil del acceso indica una tasa media `λ` vehículos/hora, el promedio esperado en un intervalo de `Δt` horas es:

`μ = λ × Δt`

Para 15 minutos, `Δt = 15/60 = 0.25 h`. Ejemplo: con `λ = 120 veh/h`, `μ = 120 × 0.25 = 30` vehículos esperados en el intervalo. Bajo el supuesto inicial de llegadas aleatorias e independientes:

`N ~ Poisson(μ)`, con `E[N] = μ` y `SD[N] = √μ`.

En este ejemplo, el conteo generado no tiene que ser 30: su media es 30 y su desviación estándar es `√30 ≈ 5.48`. Si una réplica genera `N = 28`, se sortean 28 instantes dentro de los 900 segundos del intervalo y se ordenan. Por ejemplo, `95, 420 y 818 s` podrían ser tres de esos instantes (ejemplo ilustrativo). SimPy recibe cada instante como una llegada de un vehículo individual, crea su proceso y lo mantiene en el sistema hasta que sale.

Este método representa un **proceso de Poisson homogéneo dentro de cada intervalo**. Supone una tasa constante durante esos 15 minutos; no describe por sí mismo pelotones reales entre semáforos. Más adelante podremos comparar con llegadas uniformemente espaciadas o con variación adicional si las hipótesis y los datos lo justifican. En la comparación de estrategias, se usarán exactamente los mismos conteos y tiempos de llegada por réplica: así el cambio observado se atribuye mejor al control y no a que un escenario recibió más tráfico por azar.

Los datos históricos de 33894 informan parcialmente su perfil de demanda; no son mediciones simultáneas de los otros accesos ni deben mezclarse entre campañas o años como si fueran una misma hora. Los perfiles de 33803 y 33804 tendrán que declararse como supuestos. La tasa observada de conteo también puede reflejar capacidad de descarga, por lo que no debe interpretarse automáticamente como demanda total sin revisar esa limitación.

## 2. Reglas de control a comparar

### A. Tiempos fijos independientes (referencia)

Cada intersección conserva un ciclo y una secuencia de fases predefinidos. Sus verdes y desfases quedan congelados durante la corrida y **no se calculan para favorecer el tiempo de viaje W30→W29**. Para que “independiente” sea reproducible se documentará la fase local de cada cruce y cómo se eligió; en réplicas pareadas, el calendario de referencia no cambia entre las dos estrategias comparadas. No hay detección de ocupación para cambiar el plan.

### B. Tiempos fijos coordinados por desfase (recomendada para la comparación inicial)

Se conserva el mismo ciclo, orden de fases y duración de verdes. Se modifica únicamente el desfase del plan aguas abajo para acercar su ventana de verde al tiempo de viaje desde el cruce aguas arriba. Ambos planes siguen siendo fijos durante la corrida. **Coordinar significa programar la relación temporal entre señales; no significa adaptar el plan al tráfico observado.**

Una aproximación para el desfase objetivo es:

`τ = 3.6 × L / v`,

donde `L` es la distancia en metros y `v` la velocidad de referencia en km/h; `τ` resulta en segundos. El desfase objetivo es `O_abajo = (O_arriba + τ) mod C`, donde `C` es la duración del ciclo. Ejemplo exclusivamente didáctico: si `L = 78 m`, `v = 25 km/h`, `τ = 3.6×78/25 ≈ 11.2 s`. Con ciclo de 60 s y verde aguas arriba que empieza en 0 s, se probaría desfase aguas abajo cercano a 11 s. Estos números no son todavía parámetros medidos o aprobados para el corredor.

Ejemplo de paso: supongamos un ciclo de 60 s, verde de 25 s, desfase independiente aguas abajo de 0 s y tiempo de viaje de 11 s. Un vehículo que sale de W30 en `t=20 s` llega a W29 en `t=31 s`: el verde local de 0–25 s ya terminó y esperaría al siguiente ciclo, hasta `t=60 s` (unos 29 s). Si se desplaza el inicio de ese verde a `t=11 s`, la ventana es 11–36 s y el vehículo llega dentro del verde. Es un ejemplo de un solo vehículo, sin cola ni obstrucción; no predice por sí solo el resultado del experimento.

Para que la comparación sea interpretable, se mantienen iguales: demanda y tiempos de llegada, ciclo, secuencia de fases, verdes por movimiento, amarillos y despejes, geometría, reglas de giro, almacenamiento, capacidad normal, obstrucción, colas iniciales, duración de simulación y semillas pareadas. En la estrategia coordinada cambia solo el desfase objetivo de las fases compatibles a lo largo del corredor. Se deben comparar también varios valores razonables del desfase independiente de referencia, pues una sola fase de referencia podría favorecer o perjudicar accidentalmente a una estrategia.

### C. Coordinación con regulación de acceso según ocupación (extensión adaptativa)

Esta tercera regla observa la ocupación del segmento 33802 y regula el ingreso aguas arriba: al llegar a una ocupación alta `H`, retiene vehículos antes de entrar al segmento; vuelve a permitir ingreso cuando la ocupación baja de un umbral menor `L` (`L < H`). La separación entre umbrales evita que la señal oscile rápidamente alrededor de un solo límite. El regulador debe respetar mínimos/máximos de verde, fases no conflictivas y almacenamiento físico de la cola aguas arriba.

Ejemplo didáctico: si el almacenamiento interno fuera `K=10` vehículos, se activa la retención en 8 (`H=0.8K`) y se libera al bajar a 6 (`L=0.6K`). Estos umbrales son solo para explicar la regla, no valores recomendados para la calle. La decisión aquí sí depende del estado medido del sistema: es **adaptación al estado**, distinta de sincronizar planes fijos por desfase.

**Decisión (12 nov 2026):** se compararán los tres escenarios como una escalera, donde cada escalón agrega una sola idea: A → B aísla el efecto de la coordinación fija; B → C aísla el efecto de reaccionar a la ocupación. No se comparará A directamente con C para atribuir efectos, porque cambian dos cosas a la vez. Orden de construcción: A y B primero (comparten código); C después, una vez validadas la conservación de vehículos y la obstrucción. Los umbrales de C (`H`, `L`) requerirán análisis de sensibilidad. La pregunta de investigación se reformulará para incluir C.

## 3. Conservación de vehículos y propagación de cola

Cada segmento dirigido `j` tiene una ocupación `n_j(t)` y un almacenamiento máximo `K_j`. Se debe cumplir `0 ≤ n_j(t) ≤ K_j`. La obstrucción reduce la capacidad de descarga, no elimina vehículos. En cada intento de entrada:

`espacios_j = K_j − n_j`.

Solo se admiten vehículos si hay espacio y la regla de señal/movimiento permite entrar. Los que no caben esperan en una cola aguas arriba que también cuenta para el inventario. Si esa cola alcanza la intersección anterior, se registra bloqueo de esa intersección; los vehículos siguen presentes y continúan esperando en un lugar de almacenamiento modelado. No se borran, teletransportan ni descartan.

La comprobación global de inventario es:

`vehículos generados = vehículos que salieron + vehículos en todos los segmentos + vehículos en todas las colas`.

Ejemplo: segmento lleno a 9 de `K=10`, sin salidas por obstrucción; llegan tres vehículos. Entra uno y queda ocupación 10; los otros dos permanecen en cola aguas arriba. El balance es `3 = 0 salidos + 1 dentro + 2 esperando`. La distancia y capacidad de esa cola previa deben representarse explícitamente en la topología; la red actual debe confirmar dónde esperan los vehículos si la cola sobrepasa el acceso dibujado.

La demora individual podrá definirse como `W_i = t_salida_i − t_llegada_i − t_libre_i`, donde `t_libre_i` es el tiempo de recorrido sin espera si decidimos modelarlo. La demora media de un acceso es `W̄ = (Σ W_i)/n`. Si todavía no se modela un tiempo de recorrido libre fiable, se reportará “tiempo de espera” (`inicio de servicio − llegada`) y no se llamará demora total. El tiempo promedio por sí solo no basta: también se informarán cola máxima, duración de bloqueo aguas arriba, vehículos completados y saldo en cola al final.

## 4. Diccionario de datos (aprobado el 12 nov 2026)

Sustituye la propuesta anterior de 16 variables. 19 variables: 13 en la tabla principal y 6 en la secundaria. Solo entradas comunes a A, B y C; los valores concretos (perfiles, factores, proporciones) se definen en las reglas de generación.

### Tabla `intervalos`: un acceso externo por intervalo de 15 minutos (7 × 96 × 3 = 2,016 filas)

| # | Variable | Descripción | Tipo | Escala | Unidad | Dominio |
|---:|---|---|---|---|---|---|
| 1 | `intervalo_id` | Clave única de la fila | Identificador | Nominal | — | 1 … 2,016 |
| 2 | `fecha` | Día ficticio | Fecha | Intervalo | día | 7 fechas consecutivas |
| 3 | `dia_semana` | Día de la semana | Categórica | Ordinal | — | lun < mar < … < dom |
| 4 | `tipo_dia` | Laborable o fin de semana | Categórica | Nominal | — | laborable, fin_semana |
| 5 | `hora_inicio` | Inicio del intervalo | Hora | Intervalo | HH:MM | 00:00, 00:15 … 23:45 |
| 6 | `periodo_dia` | Franja del día | Categórica | Nominal | — | madrugada, pico_am, valle, pico_pm, noche |
| 7 | `acceso_id` | Entrada externa a la red | Categórica | Nominal | — | 33804 (Séptima SB), 33803 (W30 EB), 33894 (W29 WB) |
| 8 | `lluvia` | Intensidad de lluvia | Categórica | Ordinal | — | ninguna < ligera < fuerte |
| 9 | `evento_msg` | Evento en Madison Square Garden | Binaria | Nominal | — | sí, no |
| 10 | `tasa_llegada_vph` | Tasa media esperada λ | Numérica continua | Razón | veh/h | ≥ 0 |
| 11 | `llegadas` | Vehículos llegados en el intervalo | Numérica discreta | Razón | vehículos | entero ≥ 0 |
| 12 | `prop_hacia_tramo` | Fracción que debe entrar al tramo W30–W29 | Numérica continua | Razón | proporción | [0, 1] |
| 13 | `prop_pesados` | Fracción de camiones y buses | Numérica continua | Razón | proporción | [0, 1] |

### Tabla `vehiculos`: un vehículo por fila (N = suma de `llegadas`)

| # | Variable | Descripción | Tipo | Escala | Unidad | Dominio |
|---:|---|---|---|---|---|---|
| 14 | `vehiculo_id` | Clave única del vehículo | Identificador | Nominal | — | 1 … N |
| 15 | `intervalo_id` | Llave foránea hacia `intervalos` | Identificador | Nominal | — | existe en `intervalos` |
| 16 | `segundo_llegada` | Instante dentro del intervalo | Numérica continua | Razón | s | [0, 900) |
| 17 | `fecha_hora_llegada` | Momento exacto de llegada | Fecha y hora | Intervalo | — | dentro de los 7 días |
| 18 | `tipo_vehiculo` | Clase de vehículo | Categórica | Nominal | — | auto, camion, bus |
| 19 | `movimiento` | Destino respecto al tramo | Categórica | Nominal | — | entra_tramo, otro |

### Dependencias previstas (valores por definir)

`λ = λ_base(acceso, hora, tipo_dia) × factor_lluvia × factor_evento`; `llegadas ~ Poisson(λ × 0.25 h)`; por cada llegada, una fila en `vehiculos` con `segundo_llegada` dentro del intervalo, `tipo_vehiculo` según `prop_pesados` y `movimiento` según `prop_hacia_tramo`. `evento_msg` se justifica por la cercanía de Madison Square Garden (Séptima–Octava, W31–W33). El efecto de `lluvia` será un supuesto declarado. Los patrones que se recuperen en el análisis solo verifican la generación; no son evidencia sobre Nueva York.

### Reglas de validación

- `llegadas` = número de filas de `vehiculos` con ese `intervalo_id`.
- Proporciones en [0, 1]; `llegadas` y λ no negativos; `segundo_llegada` < 900.
- `fecha_hora_llegada` = `fecha` + `hora_inicio` + `segundo_llegada`.
- `tipo_dia` coherente con `dia_semana`; `periodo_dia` coherente con `hora_inicio`.

### Fuera de estas tablas (configuración de escenarios)

Estrategia (A, B, C), ciclo, verdes, desfase, umbrales del sensor, duración y severidad de la obstrucción, almacenamiento del tramo, topología y semillas.

## 5. Reglas de generación (aprobadas el 13 nov 2026)

Implementadas y ejecutadas en `notebooks/01_datos.ipynb` (semilla maestra 20261112). Todos los valores son supuestos declarados, salvo la forma del perfil.

1. **Perfil base (veh/h, laborable):** forma = promedio horario real de 33894 (22–24 abr 2019). Séptima 33804 = 3×; W30 33803 = 0.9×; W29 33894 = 1×. Fin de semana: 0.85×, y 6:00–9:59 adicionalmente ×0.6.
2. **Tasa:** `λ = λ_base × f_fin_semana × f_día × f_lluvia × f_evento`; `f_día ~ LogNormal(0, 0.05)` por fecha y acceso.
3. **Conteo:** `llegadas ~ Poisson(λ × 0.25 h)`. Solo en entradas externas; el tramo interno lo calcula SimPy.
4. **Lluvia:** 30 % de días con un episodio de 2–5 h (inicio al azar; no pasa al día siguiente); ligera 70 % (×0.95), fuerte 30 % (×0.85); igual para los tres accesos en la misma hora.
5. **Evento MSG:** 2 noches al azar; llegada 18:00–19:45 (Séptima ×1.25, W30 ×1.10); salida 22:00–23:29 (Séptima ×1.40).
6. **Proporciones (Beta):** `prop_hacia_tramo` media 0.85 / 0.30 / 0 (concentración 200); `prop_pesados` 12 % madrugada, 5 % noche, 8 % resto (concentración 300).
7. **Vehículos:** `segundo_llegada ~ Uniforme[0, 900)` (propiedad del proceso de Poisson); tipo: auto 1−p, camión 0.7p, bus 0.3p; `movimiento` = entra_tramo con probabilidad `prop_hacia_tramo`.
8. **Calendario:** lunes 2 a domingo 8 de marzo de 2026; periodos: madrugada 0–6, pico_am 7–9, valle 10–15, pico_pm 16–19, noche 20–23.

Resultado de la corrida: 2,016 intervalos y 206,888 vehículos; todas las validaciones pasaron. Verificación pendiente en SimPy: la capacidad en condiciones normales debe superar la demanda pico (ρ < 1).

### Entradas frente a resultados de SimPy

Los 16 campos anteriores son entradas/contexto. SimPy calculará en tablas de resultado por vehículo, acceso y escenario: tiempo de llegada individual, inicio de servicio, salida, espera/demora, cola máxima y tiempo de cola, episodios y duración de bloqueo hacia W30/W29, vehículos descargados y vehículos que quedan dentro o esperando. La ocupación por segmento cambia durante la simulación y es estado del modelo; no se conoce como una medición de la fila de entrada. Un resumen podrá incluir diferencia y razón de demora entre estrategias, pero se calcularán después, junto con intervalos de incertidumbre entre réplicas.

## Decisiones que faltan antes de congelar el diccionario

1. Elegir el perfil horario sintético y los rangos plausibles de demanda de los dos accesos sin conteo.
2. Confirmar los movimientos de giro permitidos; una sola `fraccion_giro` sirve solo para dos destinos.
3. Acordar ciclos/verdes de referencia y método de selección de desfases independientes; fijar los mismos ciclos/verdes para la estrategia coordinada.
4. Definir duración/severidad de obstrucción, capacidades de almacenamiento, y destino de colas que sobrepasen los accesos representados.
5. Acordar si el parámetro `fraccion_giro` pertenece a esta tabla o a configuración, para no repetir una proporción constante en todas las filas.

Estas decisiones no se resuelven inventando precisión. Se deben explicar como supuestos, revisar rangos y hacer sensibilidad. Hasta cerrar la revisión, no generar la base.
