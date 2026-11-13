# Plan de trabajo y seguimiento del proyecto

**Nombre:** Evaluación mediante simulación de eventos discretos de estrategias de control semafórico ante condiciones de congestión vehicular en un tramo de la Séptima Avenida de Manhattan, Nueva York.

Actualizado: 12 de noviembre de 2026. Este plan organiza el trabajo; no acredita ejecución ni comprensión de etapas pendientes.

## Base documental y alcance

Se revisó el texto de las guías locales de Fase 1 (2 páginas), instalación (7 páginas), librerías (4 páginas) y programación/Fase 2 (1 página), disponibles en `guias/requisitos/`. Las figuras de la tesis deben revisarse directamente antes de adaptar su método; su correspondencia visual sigue pendiente. La guía de instalación contiene referencias mezcladas a versiones de Python: se documentará el entorno efectivo al verificarlo.

La guía exige una base ficticia con al menos 1,000 registros y 12–20 variables, o dos tablas 1:N con al menos 700 filas en la principal. No exige 5,000 registros ni 18 variables. Poisson, Gamma y lognormal aparecen como ejemplos sujetos a la lógica del sistema. Las hipótesis son opcionales en la guía. SimPy, la cantidad de réplicas y la interfaz cartográfica son decisiones del proyecto.

Los registros previos documentan auditorías de datos y una propuesta de 2,016 filas por acceso e intervalo y 16 variables. El contexto inicial proponía filas por vehículo. Son alternativas pendientes de resolver: no se mezclarán sus unidades ni se dará por cerrado el diccionario. También se definirá la diferencia entre coordinación, tiempos fijos y adaptación antes de comparar estrategias. **Decisión del 12 nov 2026:** se compararán tres escenarios en escalera (A fijos independientes, B fijos coordinados por desfase, C = B + regulación por ocupación); la pregunta y el planteamiento se reformularán para incluir C. Se conserva la pregunta de investigación registrada en `presentacion/03_pregunta_investigacion.md` como antecedente del diseño actual.

## Cómo aprenderemos en cada paso

Antes de ejecutar una operación sustantiva:

1. Explicar qué pregunta resuelve y su relación con la guía.
2. Definir conceptos, símbolos y unidades desde lo básico.
3. Presentar los supuestos y cuándo sería inadecuado usar el método.
4. Desarrollar un ejemplo pequeño, con 3–5 valores cuando corresponda, y calcularlo paso a paso.
5. Explicar la fórmula después de sus variables; mostrar las conversiones de unidades.
6. Llevar la operación a Python con código comentado y relacionarla con el cálculo manual.
7. Revisar resultados ejecutados, su interpretación y sus límites.
8. Proponer una pregunta breve de práctica y registrar dudas. Una explicación entregada no equivale a comprensión comprobada.

No todas las actividades necesitan fórmulas. Cuando una duda impida entender una decisión posterior, se resolverá antes de avanzar en esa decisión. La enseñanza se realizará durante el trabajo; este plan no sustituye las explicaciones.

## Secuencia y matriz de cumplimiento

Estados: pendiente, en curso, por verificar, terminado. «Terminado» requiere un archivo o evidencia revisable y un criterio satisfecho. Los avances anteriores se conservan como antecedentes y no se repiten sin necesidad.

| Paso | Trabajo y fundamento del curso | Matemáticas y estadística por explicar | Entregable y criterio de cierre | Estado inicial |
|---|---|---|---|---|
| 1 | Contexto del escenario: sector, proceso, actores, restricción e importancia. Fase 1, §4.1 | Sistema, límites, entradas, salidas y relación entre variables; sin fórmulas innecesarias | 1–2 párrafos y diagrama breve con entidades y flujos | Por verificar: hay antecedentes |
| 2 | Identificar fenómeno y justificar ciencia de datos + simulación. Fase 1, §4.2 | Demanda, congestión, ocupación, cola y variabilidad; distinguir descripción, predicción y evaluación de decisiones | Fenómeno observable y justificación vinculados al problema | Por verificar |
| 3 | Precisar objeto y unidad de análisis. Fase 1, §4.3 | Población modelada, observación, agregación temporal; conteo frente a tasa; relación entre acceso-intervalo y vehículo | Definición inequívoca de cada fila y su clave; resolver propuesta de unidad antes del diccionario | Por verificar: acordadas dos tablas 1:N (`intervalos` acceso × 15 min → `vehiculos`), comunes a A, B y C |
| 4 | Identificar dependientes y predictoras. Fase 1, §4.4 | Nominal, ordinal, intervalo y razón; discreta/continua; unidades, dominios, dependencias y variables derivadas | Diccionario de 12–20 variables; separar entradas sintéticas de resultados de simulación | Por verificar: diccionario de 19 variables aprobado el 12 nov (diseño técnico §4) |
| 5 | Revisar pregunta e hipótesis opcionales. Fase 1, §4.5 | Diferencia entre asociación, predicción y efecto de una política; definición medible de propagación y demora | Pregunta consistente con el objeto y comparación operacional de estrategias | Por verificar: pregunta general y tres específicas aprobadas el 12 nov 2026; hipótesis opcionales sin plantear |
| 6 | Diseñar reglas de datos sintéticos. Fase 1, §4.6 y reglas obligatorias | Variable aleatoria, probabilidad, esperanza, varianza y dependencia; Poisson para conteos, tiempos condicionados al conteo y alternativas justificadas; tasas y conversiones | Rangos, distribuciones, dependencias, claves, nulos, semillas y supuestos explicados antes de generar | Por verificar: reglas aprobadas el 13 nov (diseño técnico §5) |
| 7 | Verificar entorno Python/Jupyter. Guías de instalación y librerías | Qué aporta cada biblioteca y reproducibilidad computacional | Notebook con versiones, importaciones y figuras de Matplotlib/Bokeh; documentar Plotly/Cufflinks y cualquier ajuste | Por verificar: existe entorno, falta acreditar comprobación completa |
| 8 | Generar y validar la base ficticia. Fase 1, reglas obligatorias y §4.6 | Muestreo pseudoaleatorio, semilla, variación esperada, restricciones y coherencia entre columnas | Base que cumpla tamaño/tipos/variables elegidos, diccionario y evidencia de integridad y reproducción | Por verificar: base generada en `notebooks/01_datos.ipynb`, re-ejecutada en el `.venv` local el 13 nov |
| 9 | Adaptar la tabulación de la Figura 21 de la tesis, p. impresa 229. Programación, uso esperado 1 | Frecuencias, agrupaciones, tipos, nulos y tratamiento justificado de valores atípicos | Tabla adaptada y registro de recodificaciones/limpieza; revisar primero la figura original | Hecho en `notebooks/01c_analisis_exploratorio.ipynb` (Figuras 21–33), 13 nov |
| 10 | Describir distribuciones de al menos tres variables. Figura 22, pp. 230–231; uso esperado 2 | Media, mediana, cuantiles, varianza, desviación, IQR, histogramas y forma; ajuste de distribuciones y límites; correlación cuando corresponda | Gráficos e interpretación de forma, centro y dispersión; justificar distribuciones con evidencia | Hecho en `notebooks/01c_analisis_exploratorio.ipynb` (Figuras 21–33), 13 nov |
| 11 | Implementar modelo base. Resultados de aprendizaje de Fase 1 | Variable objetivo, predictoras, referencia simple, separación cronológica, fuga de información, MAE/RMSE y generalización limitada a datos sintéticos | Modelo sencillo comparado con referencia; evaluación ejecutada y explicada | Hecho en `notebooks/01d_modelo_base.ipynb` (Poisson, validación por día), 13 nov |
| 12 | Vincular datos con simulación. Resultados de aprendizaje de Fase 1; SimPy como decisión del proyecto | Eventos, reloj, colas, capacidad finita y conservación; llegada/descarga, espera/recorrido; parámetros calculados desde datos frente a supuestos | Motor con bitácora, parámetros trazables y verificaciones de vehículos, tiempos, fases y bloqueo | Hecho: `src/motor_simpy.py` + `notebooks/02_simulacion.ipynb`; verificado (conservación, Little, Webster, ρ), 13 nov. Falta exportar al contrato JSON |
| 13 | Diseñar y ejecutar comparación experimental. Decisión metodológica del proyecto | Escenarios comparables, semillas comunes, réplicas, censura al cierre, medias por réplica, diferencias emparejadas, intervalos de confianza y sensibilidad | Escenarios A, B y C definidos antes de ejecutar; duración de la obstrucción como factor; resultados con unidades e incertidumbre; 20–30 réplicas si es viable, justificando la elección | Hecho: `src/experimento.py` + `notebooks/03_resultados.ipynb` (540 corridas + sensibilidad), 13 nov |
| 14 | Visualizar la simulación. Decisión del proyecto | Muestreo temporal e interpolación visual; distinguir estado calculado y reconstrucción cartográfica | Interfaz que reproduzca eventos del motor y permita comprobar indicadores | Hecho: adaptador `src/adaptador_visual.py`; la maqueta reproduce A/B/C del motor SimPy (10 min, réplica 1), 13 nov. Posiciones reconstruidas, no calculadas |
| 15 | Comunicar y entregar. Programación, uso esperado 3–4 y entregables | Interpretación, límites, verificación interna frente a validación de campo; conclusiones apoyadas por cálculos | Notebook comentado y ejecutado íntegramente, HTML o PDF legible, reporte breve, datos y scripts; revisión final de esta matriz | Borrador: `docs/informe_final.md` (13 nov). Falta revisión del estudiante, confirmar supuestos y revisión final de esta matriz |

Las Figuras 23–71 (pp. impresas 232–271) se revisarán como referencia de programación para los pasos 9–11 y 15; se documentarán las adaptaciones, sin copiar la temática educativa. La numeración impresa de la tesis debe localizarse y no asumirse equivalente al índice de página del PDF.

El paso 7 es técnico y puede verificarse en paralelo a la redacción; los pasos 3–6 deben cerrarse antes de generar datos. El modelo conceptual y las métricas se afinan antes de programar SimPy. La interfaz se aborda después de disponer de eventos coherentes.

## Registro que mantendremos

- **Este archivo:** secuencia, requisito, entregable, estado y criterio de cierre. Se actualiza al cerrar o reabrir una etapa.
- **`docs/bitacora.md`:** fecha, avance/decisión, evidencia y siguiente paso; entradas breves, conservando el historial.
- **`docs/bitacora_aprendizaje.md`:** conceptos explicados, ejemplos, dudas y comprensión pendiente. Las explicaciones extensas con cálculos y código quedan en el notebook correspondiente, enlazadas desde aquí.
- **Notebooks:** pregunta → explicación → código comentado → resultado ejecutado → interpretación y límites. Conservan la evidencia del trabajo.
- **`resultados/`:** parámetros, semillas, métricas y versiones de cada experimento según la organización existente.

Al terminar cada sesión se registrará: qué hicimos, qué concepto se explicó, dónde está la evidencia, qué dudas quedan y cuál es el siguiente paso. No se anotarán cifras como resultados hasta calcularlas.

## Próxima sesión

Pasos 1–2 explicados el 12 nov (ver bitácora de aprendizaje A13–A19). Pregunta reformulada y unidad de análisis acordada. Base ficticia generada (pasos 6 y 8). Siguiente: re-ejecutar `01_datos.ipynb` en el `.venv`, instalar scipy, scikit-learn y bokeh, y empezar el análisis exploratorio de la fase 2 (pasos 9–10) al estilo de las Figuras 21–33 (propuesta: tabla principal de intervalos por acceso y tabla de vehículos, relación 1:N) antes de cerrar las variables. No regenerar históricos ni implementar el simulador para resolver esta decisión.
