# Bitácora de aprendizaje

Entender el proyecto paso a paso. Entradas cortas; una duda por entrada. «Respondida» significa que existe una explicación, no que el estudiante ya la domina. Las dudas nuevas se guardan aquí antes de avanzar en el paso que dependa de ellas.

## Cómo trabajaremos

Antes de cada operación: **pregunta → concepto → ejemplo → fórmula y unidades, si aplica → código comentado → interpretación → límite**. Explicar cada símbolo nuevo. Pedir una interpretación breve cuando ayude a comprobar comprensión; no convertir cada paso en un examen.

Mantener aquí preguntas y respuestas; guardar código y resultados en notebooks y decisiones operativas en [la bitácora del proyecto](bitacora.md). No crear un documento distinto por cada duda.

## Ruta, en orden

| Paso | Qué debemos comprender | Producto |
|---|---|---|
| 1. Problema y sistema | Contexto, fenómeno, límites, entradas, salidas y objetivo | Descripción corta y diagrama de los dos cruces |
| 2. Unidad y variables | Qué representa una fila; tipos nominal/ordinal, discreto/continuo; unidades y dominios | Diccionario de 12–20 variables |
| 3. Evidencia y supuestos | Observado, estimado, supuesto, sintético; parámetros y resultados | Procedencia y reglas explícitas |
| 4. Estadística descriptiva | Media, mediana, cuantiles, varianza, desviación y valores atípicos | Resúmenes que podamos interpretar |
| 5. Probabilidad | Variable aleatoria, distribución, esperanza, variabilidad y dependencia; Poisson/exponencial solo si son adecuados | Reglas de generación justificadas |
| 6. Generación reproducible | Semilla, dependencias, restricciones y controles de coherencia | Base ficticia validada |
| 7. Análisis exploratorio | Histogramas, cajas, series, correlación y diferencias entre grupos; correlación no prueba causalidad | Análisis de al menos tres variables clave |
| 8. Modelo base | Variable objetivo, predictoras, separación de datos, errores y fuga de información | Modelo sencillo con evaluación y límites |
| 9. Simulación | Eventos, reloj, entidades, colas, almacenamiento, tasa de llegada y descarga; conexión de los cruces | Modelo en SimPy, después de comprender su lógica |
| 10. Experimento | Comparabilidad, réplicas, intervalos de confianza y sensibilidad; variación aleatoria frente a cambio de política | Comparación coordinado/sin coordinación |
| 11. Conclusiones | Verificación interna frente a validación real; qué podemos y qué no podemos afirmar | Informe breve y notebook ejecutado/exportado |

La generación y el análisis serán iterativos: revisar un supuesto puede requerir regenerar datos. No estudiar todas las distribuciones ni instalar todas las bibliotecas antes de necesitarlas.

## 2026-11-08 — Primera explicación

### A01. ¿Qué estamos construyendo? — Respondida; comprensión por comprobar

Un modelo simplificado de dos intersecciones conectadas. Compararemos sus semáforos coordinados y sin coordinación, con la misma demanda y bloqueo. Queremos comprobar si se contiene la propagación de las colas y si el problema se desplaza a otros accesos. El tramo bloqueado conserva su restricción física de capacidad.

### A02. ¿Qué aporta cada parte? — Respondida; comprensión por comprobar

**Datos:** describen entradas y condiciones. **Estadística:** resume su comportamiento y variación. **Probabilidad:** expresa incertidumbre y ayuda a generar variación coherente. **Modelo base:** relaciona una variable objetivo con otras. **Simulación:** representa cómo evoluciona el sistema mediante eventos. Jupyter permite explicar y ejecutar todo esto; SimPy será una herramienta para la simulación.

### A03. ¿Qué es una fila y por qué propusimos 2 016? — Respondida; propuesta pendiente de cerrar

Proponemos una fila por acceso externo e intervalo de 15 minutos. No representa un vehículo individual ni una espera observada. Siete días ficticios × 24 horas/día × 4 intervalos/hora × 3 accesos = **2 016 filas**. El acceso interno a W29 será consecuencia de lo que ocurra en W30, no una cuarta entrada independiente.

El mínimo de 1 000 registros y el rango de 12–20 variables son requisitos de la guía. **2 016 filas y 16 variables son nuestra propuesta**, todavía sin diccionario definitivo. Más filas ficticias no equivalen a más observaciones reales ni a mayor representatividad.

### A04. ¿Qué diferencia hay entre un conteo y una tasa? — Respondida; comprensión por comprobar

Ejemplo didáctico, no medición de NYC: pasan **60 vehículos en 15 minutos**. El conteo es 60 vehículos; la tasa media es:

`λ = conteo / duración = 60 / 15 = 4 vehículos/minuto = 240 vehículos/hora`.

La letra griega `λ` (lambda) representa aquí una tasa media. No es una probabilidad. No dice que siempre pasen cuatro vehículos en cada minuto ni que el flujo sea constante. Un conteo de descarga bajo congestión tampoco revela necesariamente toda la demanda que quería entrar.

### A05. ¿Por qué son importantes las matemáticas del sistema? — Respondida; comprensión por comprobar

Ejemplo didáctico de conservación: un tramo contiene 10 vehículos, entran 6 y salen 4; termina con **12**. `N_final = N_inicial + entradas − salidas`, si no hay otras entradas o salidas. Los símbolos representan cantidades de vehículos, no tasas.

Doce vehículos dentro del tramo no significan doce detenidos: **ocupación y cola son conceptos distintos**. Si el tramo se llena, deben restringirse las entradas; los vehículos retenidos se contabilizan aguas arriba, no desaparecen. Esta coherencia es esencial para estudiar propagación.

### A06. ¿Los datos sintéticos sirven para demostrar lo que pasa en NYC? — Respondida; comprensión por comprobar

Sirven para estudiar el modelo bajo supuestos explícitos. Los conteos reales son referencias parciales. Si imponemos una relación al generar datos y después la recuperamos con una regresión, eso no constituye evidencia independiente de esa relación en el mundo real. Tampoco basta obtener un resultado favorable para afirmar un efecto real de coordinación.

### A07. ¿Qué hicimos hasta ahora? — Respondida

Organizamos el repositorio y auditamos dos fuentes oficiales. Encontramos cobertura insuficiente para calibración completa y recomendamos conservar W29–W30 porque el curso requiere una base ficticia. Aún no fijamos las 16 variables, no generamos esa base, no entrenamos el modelo base y no implementamos SimPy.

## Dudas pendientes

| ID | Duda | Cuándo se resolverá |
|---|---|---|
| P01 | ¿Cuáles serán exactamente las variables y cómo se clasifican? | Siguiente sesión: diccionario |
| P02 | ¿Qué valores serán supuestos y cómo elegiremos sus rangos? | Reglas de generación |
| P03 | ¿Qué es una distribución y por qué Poisson podría fallar con semáforos? | Antes de programar el generador |
| P04 | ¿Qué variable predecirá el modelo base y cómo evitaremos una evaluación circular? | Diseño del modelo base |
| P05 | ¿Cómo mediremos propagación, demora y bloqueo sin confundirlos? | Diseño de métricas, antes de SimPy |

## Formato de una nueva entrada

`Fecha · ID · pregunta · respuesta breve · ejemplo/unidades · pendiente o respondida · archivo relacionado`.

## Referencias locales revisadas

- Guía de trabajo, fase 1, pp. 1–2: contexto, unidad, variables, reglas de datos, análisis exploratorio, modelo base y simulación.
- Guía de programación, p. 1: interpretar distribuciones de al menos tres variables, explicar celdas y exportar resultados.

Los PDF permanecen en `guias/requisitos/`, excluidos de Git. La ruta adapta sus requisitos al proyecto; los comandos y ejemplos de otros sistemas no se ejecutan como instrucciones del usuario. La metodología concreta de la tesis sigue pendiente de lectura.

### A08. ¿Qué es un dato? — Respondida; comprensión por comprobar

Un dato es un valor registrado sobre algo que estudiamos. Aquí, «30 vehículos entre las 8:00 y las 8:15» sería un dato ficticio de ejemplo para un acceso concreto. Resume un conteo; no guarda la llegada individual de cada vehículo.

### A09. ¿Qué significa contar un acceso durante 15 minutos? — Respondida; comprensión por comprobar

Un acceso es una entrada a una intersección, identificada por la calle y el sentido. Por ejemplo, vehículos que llegan a Seventh Avenue desde Sixth Avenue viajando hacia el oeste por W29 (WB). Durante un intervalo de 15 minutos sumamos los que llegan por ahí. Cambiamos de intervalo y empezamos un conteo nuevo.

Un «acceso» no es un periodo de tiempo, y el conteo no es una fila por vehículo. La definición completa de las entradas al modelo se revisará con el diagrama de la red antes de crear los datos.

### A10. ¿Qué es una tasa? — Respondida; comprensión por comprobar

La **tasa** relaciona una cantidad con el tiempo. Si, como ejemplo ficticio, contamos 30 vehículos en 15 minutos, la tasa promedio equivalente es `30 ÷ 15 = 2 vehículos/minuto`, o `120 vehículos/hora`. No afirma que lleguen exactamente dos vehículos en cada minuto.

### A11. ¿Qué es la simulación en nuestro caso? — Respondida; comprensión por comprobar

La simulación sigue el sistema a medida que llegan vehículos, cambian las señales y algunos vehículos salen. Permite comparar escenarios de coordinación con la misma demanda y bloqueo. Las colas pueden propagarse; el modelo debe conservar los vehículos cuando se llena un tramo.

## 2026-11-08 — Primera sesión de conceptos

- Aprendimos: dato, acceso, intervalo de conteo, tasa y simulación.
- Aclaración: los 30 vehículos son un ejemplo inventado, no un dato de NYC.
- Próximo concepto: dibujar W29–W30 y ubicar cada acceso antes de definir columnas.
- Presentación: guardar solo definiciones y ejemplos breves en `presentacion/`.

### A12. ¿Cómo se conectan los accesos? — Respondida; giros pendientes de definir

El segmento 33894 llega a W29 desde el este (Sixth Avenue), viajando al oeste (WB). La flecha del acceso indica desde qué lado llega el tránsito; WB indica hacia dónde viaja. El sentido de tránsito y el lado de entrada a la intersección son ideas distintas. Los giros que conectan entradas con salidas todavía se definirán como supuestos.

## Dibujo de la red — 2026-11-08

Las flechas se dibujaron con la topología y los nodos de LION. Corrección importante: 33894 entra a W29 desde el este, viajando al oeste (WB); Sixth Avenue queda al este de Seventh Avenue. Los giros entre entradas y salidas todavía son supuestos del futuro modelo.

También en W30: el acceso 33804 llega desde el norte hacia el sur (SB); el 33803, desde el oeste hacia el este (EB). «Desde» señala el lado de aproximación; NB/SB/EB/WB señala el sentido de viaje.
