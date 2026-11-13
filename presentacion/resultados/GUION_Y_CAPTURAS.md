# Guion de presentación de resultados y lista de capturas

Proyecto: **Evaluación mediante simulación de eventos discretos de estrategias de control semafórico ante condiciones de congestión vehicular en un tramo de la Séptima Avenida de Manhattan, Nueva York**.

Formato propuesto: 10 diapositivas principales, aproximadamente 10 minutos, y 2 de respaldo para preguntas. La presentación se centra en resultados, no pretende sustituir los entregables del curso. El PowerPoint armado con este guion está en `presentacion_resultados.pptx` (PDF de respaldo en `presentacion_resultados.pdf`); si se modifica, este archivo sigue siendo la referencia.

## Instrucciones para quien diseñe las diapositivas

- Formato panorámico 16:9. Fondo blanco o marfil muy tenue; texto oscuro; márgenes amplios.
- Usar Aptos o una familia sans serif consistente. Títulos de 30–36 pt, cuerpo de 22–26 pt y datos/tablas de al menos 20 pt. El título académico de portada puede ocupar varias líneas a 30–32 pt.
- Una idea central por diapositiva. Un visual grande o una tabla pequeña; evitar paneles pequeños, párrafos y capturas de notebooks completos.
- El texto marcado «En pantalla» va en la diapositiva. «Guion oral» va en notas del presentador, no en el cuerpo. Las instrucciones visuales tampoco se copian a la diapositiva.
- Conservar los colores de la gráfica: A azul, B naranja y C verde. Siempre añadir las letras/nombres; el color por sí solo no basta.
- Tablas como objetos editables de PowerPoint, no fotografías. Conservar unidades y decimales. No convertir segundos en porcentajes sin calcularlos y explicar la referencia.
- Pie breve en las diapositivas de resultados: «Modelo con demanda sintética · 30 réplicas por condición». La maqueta se rotula «Una corrida ilustrativa · posiciones reconstruidas».
- Las notas deben citar el archivo/notebook de origen indicado aquí. La simulación es hipotética; la ambientación 3D no debe presentarse como una reproducción urbana validada.

## Diapositiva 1 — Portada

**Tiempo:** 25 s.

**En pantalla:** el título académico completo escrito arriba. Debajo: «Resultados del estudio · Modelación y Simulación II». Añadir los integrantes y datos académicos correctos al montar la presentación.

**Visual:** portada limpia; el título tiene prioridad. No necesita captura.

**Guion oral:**

«Estudiamos cómo responden dos intersecciones conectadas cuando una obstrucción reduce el paso de vehículos. Comparamos tres estrategias para saber cuánto esperan los vehículos y dónde termina acumulándose la cola. La ubicación sirve de contexto, pero las conclusiones corresponden a un modelo con demanda sintética».

## Diapositiva 2 — El problema: dos cruces y poco espacio entre ellos

**Tiempo:** 50 s.

**En pantalla:**

- W30 → tramo limitado → W29.
- Obstrucción hipotética: dos de tres carriles bloqueados.
- ¿Reducimos la cola o la trasladamos?

**Visual:** `capturas/02_ABC_inicio_00min.png`. Añadir rótulos legibles de W30, W29 y sentido sur; señalar el tramo con discreción. La comparación recibida está en 00:00, antes del incidente, y permite presentar la red y las estrategias.

**Guion oral:**

«No basta con mirar un semáforo por separado. Si deja pasar vehículos hacia una cuadra que ya está llena, el problema puede alcanzar el cruce anterior. Por eso estudiamos los dos cruces juntos. El incidente es hipotético y reduce el paso a un carril. Queríamos comprobar si cambiar los semáforos mejora el conjunto o simplemente mueve la espera a otra calle».

**Fuente para notas:** `notebooks/02_simulacion.ipynb`; parámetros y modelo conceptual.

## Diapositiva 3 — Las tres estrategias

**Tiempo:** 55 s.

**En pantalla:** tabla editable de tres filas.

| Estrategia | Decisión de control |
|---|---|
| A · Referencia fija | Desfase de 40 s |
| B · Coordinada | Desfase de 12 s |
| C · Regulación por ocupación | B + retención de entradas cuando el tramo se llena |

**Visual:** la tabla es suficiente. Explicar que B también usa tiempos fijos; coordinación y adaptación no son sinónimos. No añadir una captura solo para decorar.

**Guion oral:**

«A usa un horario fijo de referencia. B cambia la separación temporal entre los verdes para acompañar el recorrido de los vehículos. C conserva esa coordinación, pero añade una regla: cuando el tramo está muy ocupado, retiene entradas y deja que se vacíe. Comparamos B con A para estudiar la coordinación y C con B para estudiar lo que agrega la regulación. El desfase de A es una referencia específica, no representa todos los planes posibles».

**Fuente para notas:** `notebooks/02_simulacion.ipynb`; `docs/informe_final.md`, método.

## Diapositiva 4 — Una comparación con las mismas condiciones

**Tiempo:** 55 s.

**En pantalla:**

**540 corridas**

6 duraciones × 3 estrategias × 30 réplicas

«Mismos vehículos dentro de cada réplica»

«Diferencias emparejadas · IC del 95 %»

**Visual:** composición tipográfica amplia. No usar captura de código.

**Guion oral:**

«Una réplica es repetir la prueba con otro sorteo de llegadas. Dentro de cada repetición, A, B y C reciben exactamente los mismos vehículos. Así una estrategia no gana porque le tocó menos tráfico. Probamos obstrucciones de cero, uno, tres, cinco, diez y veinte minutos. Comparamos las diferencias entre estrategias en cada réplica y estimamos su incertidumbre. Además dejamos un periodo de vaciado y comprobamos que no quedaran vehículos pendientes en la población evaluada».

**Fuente para notas:** `notebooks/03_resultados.ipynb`, diseño, experimento e intervalos; `resultados/experimento/principal.csv`. Las 540 corridas corresponden al experimento principal, sin sumar las pruebas de sensibilidad.

## Diapositiva 5 — La coordinación redujo la espera frente al plan A

**Tiempo:** 65 s.

**En pantalla:**

«Obstrucción de 10 minutos»

| Estrategia | Espera media por vehículo |
|---|---:|
| A | 36.0 s |
| B | 23.7 s |
| C | 25.0 s |

«B − A: −12.3 s · IC 95 % [−12.6, −12.0]»

**Visual:** `materiales/02_espera_10min.png` como gráfica principal en lugar de la tabla; conservar la diferencia y su IC como llamada breve. La tabla queda como alternativa editable. No mostrar tabla y gráfica redundantes a la vez.

**Guion oral:**

«Con diez minutos de obstrucción, la espera promedio fue de 36 segundos en A y de 23.7 en B. La diferencia emparejada fue aproximadamente 12.3 segundos menos por vehículo. C quedó en 25 segundos: añadir regulación no redujo más la espera. Estos valores son promedios de corridas, no tiempos idénticos para todos los vehículos. Y la mejora depende del horario A contra el cual se compara, como veremos después».

**Fuente para notas:** `materiales/resumen.csv`, duración 10; IC calculado en `03_resultados.ipynb` y reportado en `docs/informe_final.md`. Redondeo a una cifra decimal.

## Diapositiva 6 — C protegió W30 acumulando más cola antes del cruce

**Tiempo:** 80 s.

**En pantalla:** tabla editable; obstrucción de 10 min.

| Indicador | B | C |
|---|---:|---:|
| Tiempo de bloqueo de W30 | 154.3 s | 0.0 s |
| Tiempo con cola sobre el umbral W31 | 215.0 s | 410.2 s |

«C − B: +195.2 s con cola en W31»

**Visual:** usar `materiales/03_cola_W31_10min.png` como evidencia principal y añadir la llamada «Bloqueo W30: B 154.3 s → C 0.0 s». Reservar las capturas `03_B_12min.png` y `04_C_12min.png` para respaldo si recargan la lámina. Ilustran una corrida, no las medias de la gráfica. No colocar tabla, gráfica y dos capturas juntas.

**Guion oral:**

«Este es el hallazgo más importante. C evita el bloqueo marcado en W30 porque detiene vehículos antes de que entren al tramo. Pero esos vehículos siguen existiendo: esperan aguas arriba. El tiempo con cola por encima del umbral de la cuadra anterior pasó de 215 a 410 segundos, unos 195 segundos adicionales. Son segundos acumulados de una condición de cola, no espera individual. Mantener despejado un punto puede empeorar otro. Además B tampoco mejora todos los indicadores: su bloqueo de W30 es mayor que el de A en este caso».

**Fuente para notas:** `materiales/resumen.csv`, duración 10. IC de C − B en W31: [174.3, 216.1] s. W31 es un umbral basado en almacenamiento supuesto, no una tercera intersección modelada de forma completa.

## Diapositiva 7 — Las obstrucciones largas aumentaron la espera y las colas

**Tiempo:** 65 s.

**En pantalla:** título y la gráfica, sin lista adicional. Pie: «Medias de 30 réplicas; barras de IC aproximado del 95 %».

**Visual:** `materiales/01_resultados_por_duracion.png` a todo el ancho. No necesitas capturarla: ya está incluida. Si se recrea, usar `principal.csv` y conservar la definición de los intervalos; no confundir barras por estrategia con IC emparejados de diferencias.

**Guion oral:**

«El eje horizontal muestra cuánto dura la obstrucción. A la izquierda está la espera; a la derecha, el tiempo con la cola más allá del umbral W31. Al prolongar la obstrucción, ambos problemas aumentan. Con las condiciones principales, B mantiene menor espera que A y C acumula más cola aguas arriba que B. La coordinación aporta margen, pero no elimina la restricción física. En A y B, para bloqueos largos el tramo termina llenándose».

**Fuente para notas:** `notebooks/03_resultados.ipynb`, figura principal. Sus barras usan ±1.96 errores estándar; los contrastes emparejados usan t de Student.

## Diapositiva 8 — La ventaja depende del plan de comparación

**Tiempo:** 65 s.

**En pantalla:**

«B − A en espera, con obstrucción de 10 min»

| Desfase de A | Diferencia de espera |
|---|---:|
| 0 s | −4.4 s |
| 20 s | −3.2 s |
| 40 s | −12.3 s |

«En propagación de cola, el efecto incluso cambió de signo».

**Visual:** tabla editable a partir de `materiales/sensibilidad.csv`. Reservar la captura completa para preguntas.

**Guion oral:**

«Para no elegir una referencia que favoreciera a B por accidente, probamos otros horarios de A. B redujo la espera en las tres variantes, pero el ahorro cambió: no siempre fueron doce segundos. En tiempo de cola en W31, B fue peor que A con desfase cero. Por eso nuestro resultado no es que coordinar siempre contiene la cola. Es que reduce la espera en estas variantes, mientras que la propagación depende del plan de referencia. Con solo un carril bloqueado tampoco apareció propagación en las condiciones ensayadas».

**Fuente para notas:** `materiales/sensibilidad.csv`. Contra A de desfase 0, diferencia B − A en W31 = +107.7 s, IC [79.3, 136.0]. No extrapolar a todos los planes ni todas las demandas.

## Diapositiva 9 — Alcance de los resultados

**Tiempo:** 45 s.

**En pantalla:**

- Demanda sintética y parámetros supuestos.
- Escenario de demanda de una tarde.
- Sin validación con colas observadas en campo.

**Visual:** texto amplio, sin captura.

**Guion oral:**

«El modelo tiene comprobaciones internas: conserva vehículos y se contrastó con relaciones de referencia. Eso ayuda a detectar errores, pero no demuestra que reproduzca la calle real. La demanda es ficticia, los parámetros operativos son supuestos y el experimento usa una tarde específica. La maqueta permite explicar las corridas; las posiciones son reconstruidas. Las conclusiones son válidas para el modelo y las variantes probadas».

**Fuente para notas:** `docs/informe_final.md`, limitaciones; `notebooks/02_simulacion.ipynb`, verificaciones.

## Diapositiva 10 — Qué aportó el estudio

**Tiempo:** 55 s.

**En pantalla:**

«Coordinar redujo la espera frente a las referencias ensayadas».

«Regular la entrada protegió W30 trasladando la cola aguas arriba».

**Cierre:** «La decisión depende de qué ubicación e indicador se quiere proteger».

**Visual:** composición tipográfica sencilla. No añadir gráficos repetidos.

**Guion oral:**

«Sí obtuvimos algo útil: demostramos dentro del modelo que mejorar un cruce no garantiza mejorar toda la red. La simulación permitió comparar las estrategias con las mismas entradas, repetir las pruebas y reconocer el costo de cada decisión. El aporte es identificar dónde funciona la coordinación, dónde deja de bastar y qué sacrificamos al retener entradas. Para recomendar una operación real necesitaríamos calibración de campo y un objetivo explícito que priorice los indicadores».

## Respaldo R1 — Qué significa el intervalo de confianza

No exponer salvo pregunta. Mostrar una comparación: B − A = −12.3 s; IC 95 % [−12.6, −12.0].

**Respuesta preparada:** «Restamos B menos A en cada una de las 30 réplicas. Después calculamos la media de esas diferencias y su intervalo con t de Student. El intervalo mide incertidumbre por las llegadas aleatorias del modelo. No es el rango de espera de los vehículos y no incorpora incertidumbre de todos los supuestos físicos».

**Material:** captura opcional `05_diferencias_e_intervalos.png`, del apartado 2 de resultados. Si se diseña una fórmula, usar `media de diferencias ± t × desviación de diferencias / √30`; definir las letras oralmente.

## Respaldo R2 — Datos, modelo y evidencia de ejecución

**En pantalla:** «2,016 intervalos · 206,888 vehículos · dos tablas relacionadas». Debajo, «SimPy calcula eventos; la maqueta reproduce una corrida».

**Respuesta preparada:** «Generamos una semana sintética documentada. Las tablas individuales y agregadas tienen unidades diferentes. La predicción es una evaluación de patrones de esa base; las corridas actuales usan vehículos de la base o el generador Poisson, no predicciones exportadas del notebook del modelo. El experimento principal se puede reproducir con sus semillas y parámetros».

**Material:** captura comparativa `02_ABC_inicio_00min.png`, o la tabla de estructura de datos si la solicitan. No poner código pequeño.

## Capturas recibidas y uso recomendado

Las cuatro imágenes recibidas se conservaron sin alteraciones en `capturas/`. Los nombres describen lo que realmente se ve; no se asignaron tiempos que la imagen no demuestra.

| Archivo | Contenido observado | Uso y precaución |
|---|---|---|
| `01_A_incidente_tiempo_no_visible.png` | A durante obstrucción; tablero 17/33 y fila de 6 vehículos | Ilustración del camión y los tableros. El reloj no aparece: no rotular 04:00 ni 12:00. El panel de controles ocupa la esquina superior derecha. |
| `02_ABC_inicio_00min.png` | Vista comparativa A/B/C; reloj 00:00 y sin lluvia | Presentar la red o la interfaz. No usar para demostrar diferencias durante la obstrucción. |
| `03_B_12min.png` | B a 12:00; tablero 28/33 y fila de 30 vehículos | Ilustración del estado de una corrida, con reloj visible. |
| `04_C_12min.png` | C a 12:00; tablero 14/33 y fila de 47 vehículos | Ilustra menor ocupación dentro del tramo y mayor retención aguas arriba en ese instante. |

B y C tienen el mismo tiempo visible, pero diferentes ángulos de cámara. Comparar los indicadores numéricos rotulados, sin inferir magnitudes solo por la longitud aparente de las filas. Para una comparación visual estricta se pueden repetir con el mismo encuadre; estas imágenes ya sirven como ilustraciones separadas. No es necesario repetirlas para usar las gráficas estadísticas.

No usar 28/33 o 14/33 como resultados medios del experimento: son estados instantáneos. Rotular «Corrida ilustrativa, t = 12:00; posiciones reconstruidas». Los promedios proceden de `principal.csv` y las gráficas.

Capturas técnicas de tablas e IC son opcionales: los datos ya están disponibles para crear tablas editables, sin necesidad de capturar notebooks completos.

## Material que ya está listo y no necesita captura

- `materiales/01_resultados_por_duracion.png`: gráfica original de los dos indicadores por duración.
- `materiales/02_espera_10min.png`: espera media A/B/C con obstrucción de 10 min; 30 réplicas por estrategia.
- `materiales/03_cola_W31_10min.png`: tiempo medio con cola sobre el umbral W31 para la misma condición.
- `materiales/resumen.csv`: 18 combinaciones duración/estrategia; fuente para las tablas editables de resultados.
- `materiales/sensibilidad.csv`: diferencias e IC de las variantes; fuente de la diapositiva 8.
- Fuentes originales: `resultados/experimento/principal.csv`, `notebooks/03_resultados.ipynb` y `docs/informe_final.md`.

## Entrega al compañero

Compartir toda la carpeta `presentacion/resultados/`, incluyendo este archivo, `capturas/` y `materiales/`. El compañero debe:

1. Armar las diez diapositivas usando únicamente «En pantalla» y los visuales seleccionados.
2. Copiar los guiones orales en las notas del presentador y conservar allí las fuentes de cada diapositiva.
3. Mantener las unidades y los nombres A/B/C en todos los gráficos y tablas.
4. Revisar que el texto se lea desde el fondo de un salón; si algo no cabe, recortar texto antes de reducir fuentes.
5. Guardar un PowerPoint editable y un PDF de respaldo.

Antes de cerrar, comprobar que las capturas pertenecen a corridas SimPy y que no se confunden imágenes de una corrida con promedios de 30 réplicas. No afirmar que el control C elimina la congestión ni que B siempre reduce la propagación.
