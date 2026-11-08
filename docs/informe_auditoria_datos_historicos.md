# Auditoría — Seventh Avenue, W29–W30

> Actualización del 8 de noviembre: se cerró la búsqueda complementaria. Para el curso se recomienda conservar el corredor con una base ficticia; ver [decisión de ubicación](decision_ubicacion.md). Esta primera auditoría evalúa suficiencia histórica para calibración.

**Conclusión: necesitamos otra fuente para mantener las dos intersecciones con entradas fundamentadas en datos.** La ubicación sigue provisional.

Fecha: **7 de noviembre de 2026 (Guatemala)**. Fuente: [NYC DOT, Automated Traffic Volume Counts](https://data.cityofnewyork.us/Transportation/Automated-Traffic-Volume-Counts/7ym2-wayt). [Notebook reproducible](../notebooks/01_auditoria_datos_historicos.ipynb).

## Segmentos identificados

Se contrastaron nombres, 809 combinaciones agregadas de Manhattan y geometrías de [LION oficial](https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/ArcGIS/rest/services/LION/FeatureServer/0). Los nodos **21334 (W29)** y **21335 (W30)** delimitan **33802**. La consulta por ID no restringió borough.

| ID | Tramo y función | Registros |
|---|---|---:|
| 33804 | Seventh/W30–W31; entrada SB a W30 | 0 |
| 33803 | W30/Eighth–Seventh; entrada EB a W30 | 0 |
| 33802 | Seventh/W29–W30; central y entrada SB a W29 | 0 |
| **33894** | **W29/Sixth–Seventh; entrada WB a W29** | **288** |
| 33800 | Seventh/W28–W29; salida SB | 0 |
| 33801 | W29/Seventh–Eighth; salida WB | 0 |
| 33896 | W30/Seventh–Sixth; salida EB | 0 |

Son **1 de 4 accesos direccionales observados** (tres externos y uno interno), con **0 intervalos simultáneos de los cuatro**. El tramo interno depende de W30; no es una llegada externa independiente.

## Cobertura y calidad

- **33894:** solo **abril de 2019**, del **22 al 24**, lunes a miércoles; **3 días completos**, 96 intervalos/día, **288/288 esperados**; dirección **WB**, solicitud/campaña proxy **30130**. No hay otros periodos.
- Volumen: **10–112 vehículos/15 min**, media **66,12**; total **19 043**. Totales diarios: **5 759, 6 457, 6 827**. Las **72 horas completas** registran **62–425 veh/h**, media **264,49**. Solo hay tres días por hora.
- Descarga filtrada: **12 739 filas, 25 segmentos, 13 páginas**; **0,68 % de 1 875 154** registros globales. Totales verificados por ID; búsqueda cercana hasta 915 m, precedida por agregaciones.
- En lo descargado: **0 nulos, duplicados exactos/de clave, solapamientos, conflictos de volumen, fechas/minutos inválidos y volúmenes negativos/no enteros**. Hay **230 ceros**, ninguno en 33894; su causa no se deduce.
- El adjunto oficial de errores no menciona estos IDs. Advertencia adicional: **33662, Ninth Avenue**, tiene **576 registros EB/WB** pese a su geometría longitudinal; no usar sin aclaración.
- Otros segmentos tienen discontinuidades/días parciales, detallados en CSV. `requestid` es proxy de campaña; no garantiza independencia. Cobertura nominal: 96 intervalos/día; no resuelve horario de verano.
- ATR refiere a LION 14; la red actual es otra versión. Los puntos principales coinciden con sus líneas (<0,01 m). El CRS ATR no está declarado; se interpreta por correspondencia con EPSG:2263 de LION. Verificar compatibilidad histórica.

## Alternativas cercanas

| Candidata | Evidencia | Límite |
|---|---|---|
| **33821**, Seventh/W35–W36; ~479 m | 672 SB; 7 días completos, 31 jul.–6 ago. 2017 | Conserva avenida; transversales sin cobertura integral demostrada. |
| **33656**, Eighth/W30–W31; ~285 m | 672 NB; 7 días completos, 7–13 jul. 2017 | Paralela cercana; no acredita todos sus accesos. |
| **33913**, Sixth/W33–Broadway; ~408 m | 672 NB; 7 días completos, 7–13 nov. 2021 | Más reciente; tampoco acredita ambos cruces. |
| **33639/32830/33638**, Seventh/W23; ~474–534 m | 790 SB/110 WB/112 EB; septiembre 2011; **95 intervalos y 23 horas completas comunes** | Alternativa para una intersección; no resuelve dos cruces. |

Ninguna queda aprobada como nueva ubicación.

## Viabilidad para SimPy

| Categoría | Alcance |
|---|---|
| Observado | Conteos, fecha/hora, sentido, solicitud y ubicación. |
| Estimable | Perfil horario y variación entre tres días del acceso WB. El flujo observado puede estar limitado por descarga; no equivale necesariamente a demanda de llegada. |
| Por conseguir o asumir | Llegadas dentro del intervalo, platoones, giros, verdes/ciclos/desfases, saturación, almacenamiento, recorridos y bloqueo. Poisson/exponencial sería una hipótesis. |
| No inferible aquí | Trayectorias, espera real, colas observadas, demanda no satisfecha, capacidad bajo bloqueo y efecto causal de coordinación. |

**Siguiente paso:** buscar aforos complementarios de accesos/giros en NYC DOT, el [archivo histórico](https://data.cityofnewyork.us/Transportation/Traffic-Volume-Counts-Historical-/btm5-ppia) o campo; esas fuentes aún no se auditaron. Para validar propagación harán falta también señales, bloqueo y colas observadas.

Consultas [SODA 3.0](https://dev.socrata.com/docs/queries/) con Python/`requests`; App Token solo en encabezado, Secret Token sin uso. Consultas, respuestas, CSV y cuatro figuras: `resultados/auditoria_historicos/` (local). No se generaron datos sintéticos ni se implementó SimPy.
