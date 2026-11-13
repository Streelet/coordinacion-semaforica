# Informe breve · Coordinación semafórica ante una obstrucción en la Séptima Avenida (W30–W29)

13 de noviembre de 2026 · Proyecto Final MS2

> **Advertencia principal.** La demanda es **ficticia**. Se generó con reglas declaradas a partir de la forma del conteo real de 2019 del acceso 33894. Los tiempos de semáforo, carriles y capacidades son **supuestos**. Las conclusiones describen el comportamiento de **este modelo** y sirven como verificación interna, no como validación de campo. Ningún resultado debe leerse como una predicción del tráfico real.

## 1. Pregunta

¿En qué medida la coordinación semafórica y la regulación según la ocupación del tramo contienen la propagación de colas ante una obstrucción temporal en la Séptima Avenida, entre W29 y W30?

1. ¿Cuánto retrasa la coordinación por desfase (B) la llegada de la cola a W30, frente a tiempos fijos independientes (A)?
2. ¿Qué agrega la regulación por ocupación (C) a la coordinación (B) en la extensión y duración de las colas y en el verde desaprovechado?
3. ¿Cómo cambian estos efectos con la duración de la obstrucción? ¿La cola se traslada a otros accesos?

## 2. Método (en una página)

| Etapa | Qué se hizo | Dónde |
|---|---|---|
| Datos | Una semana ficticia: 2,016 intervalos (acceso × 15 min) y 206,888 vehículos. Llegadas de Poisson con λ = base × fin de semana × día × lluvia × evento | `notebooks/01_datos.ipynb` |
| Exploración | Estructura, distribuciones, normalidad (Anderson-Darling programado a mano) y tiempos entre llegadas exponenciales (CV 1.05) | `notebooks/01c_analisis_exploratorio.ipynb` |
| Modelo base | Regresión de Poisson de las llegadas, validada dejando fuera un día completo. MAE 9.7 contra 10.0 de la referencia; piso de ruido 7.5 | `notebooks/01d_modelo_base.ipynb` |
| Motor | SimPy mesoscópico: 4 filas FIFO y un tramo con almacenamiento finito K = 33. La obstrucción es un camión **atravesado que tapa 2 de los 3 carriles**: el tramo sale por 1 solo carril | `src/motor_simpy.py`, `notebooks/02_simulacion.ipynb` |
| Verificación | Conservación en cada instante; ley de Little (error < 2 %); Webster (−6 %); ρ ≤ 0.72 en condiciones normales y 1.94 con obstrucción | `tests/test_motor_simpy.py` |
| Experimento | 6 duraciones (0–20 min) × 3 estrategias × 30 réplicas con números aleatorios comunes. Diferencias emparejadas con IC 95 % y sensibilidad de 3 supuestos | `src/experimento.py`, `notebooks/03_resultados.ipynb` |
| Visualización | Maqueta 3D que reproduce A, B y C del motor; las posiciones se reconstruyen a partir de los tiempos | `visualizacion/`, `src/adaptador_visual.py` |

**Estrategias.** Las tres comparten un ciclo de 60 s, con 28 s de verde para la avenida y 22 s para la calle.
- **A:** desfase de W29 de 40 s, elegido sin mirar el tiempo de viaje.
- **B:** desfase de 12 s, que es el tiempo de viaje libre del tramo (τ = 11.5 s).
- **C:** B más un sensor de ocupación con histéresis (H = 0.8K, L = 0.6K). Al activarse, retiene la entrada al tramo y pasa el verde de la avenida a W30.

## 3. Resultados

### Cómo leer esta sección

Una réplica repite el experimento con nuevas llegadas ficticias; A, B y C reciben los mismos vehículos dentro de esa réplica. Las tablas resumen 30 réplicas por estrategia y duración.

- **Espera media:** segundos que espera un vehículo, promediados primero en cada corrida y después entre réplicas.
- **Tiempo con cola en W31:** segundos acumulados durante los que la cola supera el almacenamiento supuesto de la cuadra anterior. No es la espera de un vehículo ni una simulación de un tercer cruce.
- **Tiempo hasta llenarse:** primera detección después de las 17:00; se resume solo entre réplicas donde ocurre. Debe leerse junto al porcentaje de ocurrencia, no asignar cero a los casos sin suceso.
- **Diferencia B − A o C − B:** resta entre estrategias emparejadas por réplica. Para espera o duración de cola, un valor negativo representa una reducción.
- **IC 95 %:** incertidumbre estimada sobre la diferencia media del modelo bajo los supuestos estadísticos; no contiene al 95 % de los vehículos ni incorpora la incertidumbre de los parámetros reales.

**Ejemplo de lectura: obstrucción de 10 min.** A, B y C registran 36.0, 23.7 y 25.0 s de espera media. B − A ≈ −12.3 s indica menor espera con B frente a esa referencia A; C − B ≈ +1.3 s indica más espera al añadir la regulación. C elimina el bloqueo marcado en W30, pero aumenta el tiempo con cola en W31 de 215.0 a 410.2 s: unos 195 s adicionales. Protege una ubicación reteniendo vehículos en otra. Estos valores redondeados no sustituyen los cálculos emparejados sin redondear.

El desarrollo matemático, los ejemplos manuales y la explicación de cada operación están en `notebooks/03_resultados.ipynb` y su exportación HTML.


Escenario: miércoles de 16:30 a 18:30, con la obstrucción a las 17:00. Cada valor es la media de 30 réplicas, y las diferencias van con su intervalo de confianza del 95 %.

| Duración | Espera media A / B / C (s) | B − A espera | Tramo lleno a los… (A / B, min) | Cola en W31: A / B / C (s) | C − B en W31 (s) |
|---|---|---|---|---|---|
| 0 min | 27.5 / 15.7 / 15.7 | −11.9 [−12.0, −11.7] | — | 0 / 0 / 0 | 0 |
| 3 min | 28.2 / 16.4 / 16.7 | −11.8 [−12.0, −11.6] | 2.3 / 2.2 (lleno en 70 % / 57 % de las réplicas) | 0 / 0 / 7 | +6.5 [0.3, 12.7] |
| 5 min | 29.6 / 17.7 / 18.3 | −11.9 [−12.1, −11.7] | 2.5 / 3.2 | 14 / 4 / 61 | +56.7 [35.6, 77.8] |
| 10 min | 36.0 / 23.7 / 25.0 | −12.3 [−12.6, −12.0] | 2.5 / 3.2 | 295 / 215 / 410 | +195.2 [174.3, 216.1] |
| 20 min | 62.1 / 47.4 / 50.8 | −14.8 [−15.3, −14.2] | 2.5 / 3.2 | 1,179 / 1,019 / 1,236 | +216.8 [192.1, 241.6] |

**Respuesta 1 (A → B).** Con obstrucciones de 5 min o más, la coordinación retrasa unos **40 s** el llenado del tramo (de 2.5 a 3.2 min). Ese margen solo decide algo en bloqueos cortos: con 5 min, la cola llega a W31 en el 30 % de las réplicas de A y solo en el 7 % de las de B. En bloqueos largos, todo termina lleno. Además, B reduce la espera de forma robusta. **Pero** el tamaño del efecto depende del plan A de referencia: −12 s contra un desfase de 40 s y solo −3 a −4 s contra 0 o 20 s. En el contagio a W31, el signo incluso **se invierte** contra el desfase de 0 s (+108 s). La afirmación "coordinar contiene la cola" no es robusta en este modelo.

**Respuesta 2 (B → C).** C nunca llena el tramo y elimina el bloqueo físico de W30: el verde desaprovechado baja de 154 s a 0 con 10 min de obstrucción. A cambio, **traslada** la cola a la cuadra anterior: llega a W31 antes y se queda más tiempo (+195 s con 10 min). Esto ocurre con los tres pares de umbrales probados; el daño es menor cuanto más alto es H.

**Respuesta 3 (duración y traslado).**
- Hasta 3 min, la obstrucción casi no se nota en W31.
- Desde 5 min, la cola sube por la Séptima. Los efectos de B y C crecen con la duración.
- La calle W30 hacia el este paga una parte del traslado en B (≈ +5 s de espera frente a A) y gana un poco con C (−1.3 s frente a B), porque recibe el verde que C quita a la avenida.
- Con un solo carril bloqueado (por ejemplo, un camión estacionado en doble fila) no hay contagio, porque la salida del tramo conserva ρ < 1. El fenómeno requiere una obstrucción que tape 2 carriles, como un camión atravesado, una avería o una obra.

## 4. Conclusión

En este modelo, **la coordinación da margen, no inmunidad**: retrasa el llenado del tramo y reduce la espera, pero no impide el *spillback* en obstrucciones largas, y su efecto sobre la cola depende del plan de referencia. **Reaccionar a la ocupación protege el cruce de W30 trasladando la cola hacia arriba**, no reduciéndola. Que eso convenga depende de qué se quiera proteger: el cruce, que mantiene libre el paso transversal, o la cuadra anterior.

## 5. Limitaciones

1. **Datos ficticios.** Los patrones confirman las reglas del generador. Solo la forma horaria de 33894 proviene de mediciones reales (2019; ver sección 7).
2. **Parámetros supuestos:** ciclo, verdes, carriles, saturación de 1,800 veh/h por carril, PCE de 1.5, 25 km/h y 7 m por vehículo. Los resultados son sensibles al desfase de A, a los umbrales de C y a la severidad de la obstrucción.
3. **Modelo mesoscópico:** colas FIFO sin carriles individuales; la avenida es un almacén agregado. El FIFO en la Séptima hace que quien gira hacia W30 también espere detrás de quien va al tramo (supuesto conservador).
4. **Cumplimiento total** de "no bloquear el cruce". No hay peatones ni giros con conflicto.
5. **Un solo escenario de demanda** (miércoles por la tarde). No se probaron la lluvia ni el evento del MSG en la simulación.
6. **Visualización:** las posiciones de la maqueta son una reconstrucción visual. Las métricas sí son del motor.
7. **Verificación ≠ validación.** El motor cumple conservación, Little y Webster, pero no se ha contrastado con observaciones de campo.

## 6. Cómo reproducir

```bash
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01_datos.ipynb notebooks/01c_analisis_exploratorio.ipynb notebooks/01d_modelo_base.ipynb notebooks/02_simulacion.ipynb notebooks/03_resultados.ipynb
.venv/bin/python src/adaptador_visual.py --salida visualizacion/public/datos/simpy
```

Semillas: base 20261112 y réplicas 20261113 + r. Los HTML de cada notebook están junto al `.ipynb`.

## 7. Fuentes de datos

Datos reales usados como referencia (portal oficial de datos abiertos de la Ciudad de Nueva York):

1. NYC Department of Transportation. (2021). *Automated Traffic Volume Counts* (ID `7ym2-wayt`) [Conjunto de datos]. NYC Open Data. https://data.cityofnewyork.us/Transportation/Automated-Traffic-Volume-Counts/7ym2-wayt. Consultado el 7 de noviembre de 2026.
   - **Registros usados:** segmento `33894` (West 29 Street, de 6 Avenue Line a 7 Avenue, sentido WB), 22–24 de abril de 2019: 288 intervalos de 15 min. Con ellos se calculó el perfil horario que alimenta el generador.
   - **Descarga directa de esos registros (CSV):** https://data.cityofnewyork.us/resource/7ym2-wayt.csv?segmentid=33894&yr=2019&m=4
2. NYC Department of Transportation. (2022). *Traffic Volume Counts (Historical)* (ID `btm5-ppia`) [Conjunto de datos]. NYC Open Data. https://data.cityofnewyork.us/Transportation/Traffic-Volume-Counts-Historical-/btm5-ppia. Consultado el 8 de noviembre de 2026.
   - **Uso:** tres referencias cercanas (78 filas diarias, 2012–2020) solo para contrastar la plausibilidad; no son accesos exactos del tramo y no entran al modelo.

Datos generados por el proyecto (no publicados en línea): `datos/procesados/intervalos.csv` (2,016 filas) y `datos/procesados/vehiculos.csv` (206,888 filas), producidos por `notebooks/01_datos.ipynb` con la semilla 20261112. Se conservan localmente; se regeneran ejecutando ese notebook. Detalle de procedencia: `datos/fuentes.csv`; auditorías: `notebooks/01_auditoria_datos_historicos.ipynb` y `notebooks/01b_auditoria_historico_complementario.ipynb`.
