# Cierre de auditoría y recomendación de ubicación

**Recomiendo mantener Seventh Avenue entre W29 y W30 y comenzar una base ficticia con supuestos explícitos.** Se cierra la búsqueda histórica. La calibración incompleta limita las conclusiones empíricas, pero no impide cumplir el proyecto académico.

Consulta: **8 de noviembre de 2026**. [Notebook reproducible](../notebooks/01b_auditoria_historico_complementario.ipynb). Fuentes oficiales: [histórico `btm5-ppia`](https://data.cityofnewyork.us/Transportation/Traffic-Volume-Counts-Historical-/btm5-ppia) y [ATR `7ym2-wayt`](https://data.cityofnewyork.us/Transportation/Automated-Traffic-Volume-Counts/7ym2-wayt).

## Resultado de la última búsqueda

| Ubicación | Datos primarios confirmados | Aporte del histórico |
|---|---|---|
| W29–W30 | **288 intervalos de 15 min**, WB en **33894**, 22–24 abril 2019. Los otros seis tramos: **0**. | **0 días adicionales** en los siete tramos. |
| Seventh/W23 | **790 SB / 110 WB / 112 EB**, septiembre 2011. Coinciden **95 intervalos**, equivalentes a **23 horas completas simultáneas** más intervalos parciales. | **0 días adicionales** en sus tres accesos ni en la salida SB. |

En W29–W30 continúa observado **1 de 4 accesos direccionales**; ninguno de los dos accesos a W30 tiene registros. Los IDs se contrastaron con geometrías y con todos los segmentos de calle conectados a los nodos LION **21334, 21335 y 21247**. El histórico no contiene geometría propia; no basta una coincidencia de nombre.

## Referencias cercanas encontradas

| ID / ubicación real según LION | Sentido | Días por bloque |
|---|---|---|
| **33652**, Seventh/W27–W28 | SB | 8 en 2012; 9 en 2017; 9 en 2020 |
| **33891**, W29/Fifth–Broadway | WB | 8 en 2012; 9 en 2016; 9 en 2019 |
| **34013**, W30/Fifth–Broadway | EB | 8 en 2012; 9 en 2017; 9 en 2020 |

Son **78 filas diarias / 1 872 conteos horarios nominales**, separados en **nueve bloques**. Fechas exactas y rangos de volumen: notebook y `bloques_historicos.csv`. Solo los bloques del **30 septiembre–7 octubre de 2012** coinciden en las tres referencias: **192 horas nominales**. Son otros tramos y no coinciden con abril de 2019; no completan los accesos originales.

Se conservaron **nueve etiquetas discrepantes** en 33652/2020: dicen East 27/28, mientras el ID corresponde a West 27/28. No usarlas como referencia principal sin aclaración. Count ID no demuestra una campaña global ni independencia.

## Duplicaciones y calidad

En **78 filas históricas** y **1 300 primarias** filtradas: **0 nulos, duplicados exactos/de clave y volúmenes inválidos**. Al comparar por **segmento, sentido, fecha y hora**, agregando solo horas primarias con cuatro cuartos completos, hubo **0 coincidencias entre fuentes**. No se detectaron duplicaciones comparables en este subconjunto; no se afirma independencia de los datasets completos.

## Decisión entre las tres opciones

| Opción | Evaluación |
|---|---|
| **1. Mantener W29–W30 con supuestos sintéticos** | **Recomendada.** Conserva dos semáforos y el objetivo de contener propagación. El curso admite datos ficticios. |
| 2. Reducir a Seventh/W23 | Tiene accesos observados, pero poca simultaneidad. Una sola intersección cambia la pregunta de coordinación entre semáforos. |
| 3. Cambiar de lugar | En esta búsqueda acotada no se demostró una mejora integral en otro corredor de dos cruces. No justifica prolongar la búsqueda. |

**Inicio propuesto:** **2 016 registros ficticios y 16 variables**: 7 días ficticios × 96 intervalos × 3 entradas externas. Cumple el mínimo de 1 000 registros y 12–20 variables indicado para el curso. El acceso interno a W29 debe depender de W30; no generar una cuarta demanda independiente.

Usar 33894 como referencia histórica parcial; declarar como supuestos las demás entradas, giros, señales, almacenamiento y bloqueo. Contrastar plausibilidad con cada bloque cercano por separado. La comparación futura usará la misma demanda y bloqueo, réplicas y sensibilidad; no atribuirá validación real a los datos ficticios ni un aumento de capacidad al tramo bloqueado.

No se generaron datos sintéticos ni se implementó SimPy. Respuestas, consultas y CSV permanecen locales en `resultados/auditoria_historico_complementario/`; credenciales excluidas.
