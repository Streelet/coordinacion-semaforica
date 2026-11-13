# Conexión motor → visualización (v1)

```text
Entradas → motor Python/SimPy → exportacion_visual.py → JSON + manifest.json
                                                       ↓ solo lectura
                                      fuenteCorridas.js → componentes 3D
```

El motor decide llegadas, fases, colas, restricciones y métricas. La página interpreta los registros y elige cámara, colores, modelos, lluvia visual y controles. Cambiar esos elementos gráficos no vuelve a ejecutar el motor ni escribe sus archivos.

## Qué debe exportar el motor

- `reproduccion.schema.json`: formato compartido, validado por Python y JavaScript.
- `manifiesto.schema.json`: tres referencias A/B/C, con nombres relativos a `manifest.json`.
- `ejemplo_A.json`: registro mínimo válido, ilustrativo; no es un resultado del proyecto.

Cada corrida declara versión `1.0`, motor, identificador de entradas comunes (`entradas_id`), réplica, estrategia y duración. Unidades: segundos y metros; plano x al este/y al norte. Cada punto vehicular `[t, s]` indica tiempo y distancia acumulada del **frente** sobre su ruta. Puede incluir una muestra posterior al horizonte para interpolar el cierre; la reproducción termina en `meta.duracion`.

El cargador rechaza versiones incompatibles, IDs duplicados, referencias inválidas, tiempos desordenados y series desalineadas. También comprueba que A/B/C declaren la misma red, duración, réplica e identificador de entradas. Este identificador es una referencia: su coincidencia no demuestra por sí sola que el motor haya usado entradas idénticas.

## Uso desde Python

Importar desde `src` (en un notebook, añadir esa carpeta a `sys.path`):

```python
from exportacion_visual import exportar_corrida, exportar_manifiesto

# registro: eventos, geometría y métricas ya calculados por el motor.
exportar_corrida(registro, carpeta / 'A.json', motor='simpy',
                 entradas_id='base-20261112', replica_id=1)
# Después de exportar también B y C:
exportar_manifiesto([{'id': e, 'archivo': f'{e}.json'} for e in 'ABC'],
                    carpeta / 'manifest.json')
```

`exportar_corrida` añade versión/unidades y valida antes de escribir; usa sustitución atómica y no modifica el diccionario recibido. El motor elige la carpeta de salida. Para publicar una corrida, copiar los cuatro archivos al directorio servido por la web y apuntar `FUENTE_CORRIDAS` a su manifiesto. No sobrescribir archivos publicados de una corrida en uso: usar una carpeta distinta por corrida.

## Límites que deben conservarse explícitos

- El contrato v1 reproduce este corredor y sus dos fases avenida/transversal; no es un formato general para cualquier red vial.
- `src/adaptador_visual.py` convierte las corridas del motor SimPy a este formato. Los tiempos, luces, regulación y métricas son del motor; las posiciones en metros se reconstruyen a partir de los instantes de cruce y del puesto en cada fila.
- Los resultados/semáforos se leen del archivo. `color` y `radio_giro` son opciones gráficas y se pueden omitir.
- `metricas.t` comienza en cero y es creciente; cada serie tiene la misma longitud. La página usa la última muestra disponible, sin asumir frecuencia de 1 Hz.
- Por compatibilidad con la demo, `salidas_tramo` cuenta rutas completadas que recorrieron el tramo; todavía no equivale al cruce de su límite. `t_cola_llega_w30` es la primera detección, no un estado actual. Deben revisarse esas métricas al integrar el motor definitivo.
- Validar el contrato no verifica conservación, calibración o seguridad de fases. Esas comprobaciones corresponden al motor. Clima y camión decorativos de la demo siguen siendo representación; no recalculan resultados.

Comprobaciones: `.venv/bin/python -m unittest discover -s tests` y `npm --prefix visualizacion test`. Ambos lenguajes comparten casos válidos/incorrectos de esta carpeta.
