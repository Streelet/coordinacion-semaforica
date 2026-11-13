# Visualización de la simulación

Maqueta 3D animada de la Séptima Avenida entre W29 y W30. Muestra las estrategias A, B y C lado a lado, con el mismo tráfico y la misma obstrucción.

**La página no simula nada.** Solo lee un archivo por estrategia con lo que calculó el modelo en Python y lo dibuja. Lee por defecto las corridas del motor SimPy (`public/datos/simpy/`): obstrucción de 10 min, réplica 1, ventana de 30 min. La demanda es ficticia y las posiciones en metros son una **reconstrucción** del adaptador (el motor calcula tiempos y colas, no trayectorias). La Séptima se dibuja con 3 carriles, como en el motor, y cada vehículo guarda su largo + 2.5 m del de adelante. Los datos de demostración siguen en `public/datos/demo_*.json`; para verlos, cambiar `FUENTE_CORRIDAS` en `src/config.js`.

## Cómo abrirla

Se necesita Node.js 20 o más reciente.

```bash
cd visualizacion
npm install        # solo la primera vez
npm run dev        # abre la dirección que aparece, normalmente http://localhost:5173
```

Para regenerar las corridas SimPy (opciones `--duracion` y `--replica`), desde la raíz del proyecto:

```bash
python src/adaptador_visual.py --salida visualizacion/public/datos/simpy
```

Para regenerar los datos de demostración:

```bash
python src/demo_animacion.py --salida visualizacion/public/datos
```

## Controles

- Reproducir / pausar, reiniciar, velocidad (×1, ×4, ×10, ×30) y barra de tiempo.
- **Comparar** muestra A, B y C a la vez; los botones A, B y C muestran una sola en grande.
- Con el ratón: rueda para acercar, arrastrar para girar, clic derecho para desplazar.

## Qué se ve

- Las **líneas de alto** y las esferas de los postes tienen el color de la luz de ese acceso.
- El **camión rosado con conos** es la obstrucción; aparece solo mientras dura.
- En la estrategia C, la franja sobre el tramo es el **sensor**: se pone naranja cuando regula el ingreso.
- La tarjeta de cada panel muestra los carros en el tramo, si la cola ya llegó a W30, el verde desaprovechado y cuántos carros salieron.

## Modelos de Kenney incluidos

Selección local de 17 modelos de los cuatro paquetes proporcionados (CC0):

- Car Kit: seis autos, camión y vehículo de obstrucción.
- City Kit Commercial: cuatro edificios.
- Nature Kit: tres árboles.
- City Kit Roads: conos y farolas.

Archivos, texturas y licencias en `public/modelos/`, separados por paquete para evitar colisiones de texturas. Selección en `src/config.js`. El autobús conserva el modelo de la plantilla porque el Car Kit no incluye uno. Las calles mantienen la geometría del registro de demostración; la ambientación es ilustrativa y no una reconstrucción urbana validada.

Comprobación del 13 nov 2026: compilación correcta, 17 GLB accesibles y texturas presentes; reproducción, pausa, barra temporal y comparación A/B/C comprobadas en navegador sin errores de consola. Evidencia: `../resultados/visualizacion/modelos_kenney.png`.

## Formato del archivo de cada escenario

Es el contrato entre Python y la página. El exportador de SimPy debe producir esto mismo. Unidades: metros y segundos; `x` hacia el este, `y` hacia el norte.

| Clave | Contenido |
|---|---|
| `meta` | `estrategia`, `nombre`, `duracion`, `es_demo`, `parametros` |
| `red.rutas` | por ruta, lista de puntos `[x, y]`; `red.radio_giro` redondea las esquinas |
| `red.calles`, `red.nodos`, `red.lineas_alto`, `red.tramo` | geometría que se dibuja y capacidad del tramo |
| `semaforos` | por cruce, cambios `[t, avenida, transversal]` con `"V"`, `"A"` o `"R"` |
| `regulacion` | cambios `[t, 1 o 0]` de la regulación de la estrategia C |
| `obstruccion` | `t_inicio`, `t_fin` y posición del camión |
| `vehiculos` | `id`, `tipo` (`auto`, `camion`, `bus`), `color`, `ruta` y puntos clave `k` = `[t, distancia recorrida en la ruta]` |
| `metricas` | muestras con tiempos explícitos en `t`: `ocupacion_tramo`, `verde_perdido`, `salidas_tramo`, `cola_norte` |
| `resumen` | `t_cola_llega_w30` (o `null`), totales |

Entre dos puntos clave la página interpola en línea recta, así que solo hace falta guardar un punto cuando cambia la velocidad. La distancia corresponde al frente del vehículo.

Para conectar otro motor: exportar archivos con el contrato v1 y publicar su `manifest.json`. El manifiesto contiene las rutas relativas de A/B/C; `FUENTE_CORRIDAS` en `src/config.js` señala a ese único punto de entrada. Ver [contrato y ejemplo de exportación](../contratos/README.md).

## Límites de la demostración

Un carril por calle, demanda constante, 12 minutos, sin validación. El simulador de juguete (`src/demo_animacion.py`) existe solo para tener movimiento con el cual armar la animación y fijar el formato.

## Reglas de presentación

- Mantener indicadores y controles de la interfaz fuera del canvas. Excepción solicitada: dos paneles físicos 3D al costado del tramo muestran paso normal/reducido y su estado activo; permanecen fuera de la calzada.
- Fondo blanco, tipografía Nunito local (licencia OFL en `public/fonts/`) y paleta azul intenso, gris frío, verde y rojo funcionales. Evitar pasteles y tonos tierra en la interfaz.
- Cámara inicial oblicua elevada centrada en W29–W30; encuadre ajustado al tamaño de cada panel para priorizar ambos cruces y el tramo interno.

## Lluvia visual

Selector exterior: sin lluvia, lluvia ligera y lluvia intensa, común a A/B/C. La intensa incorpora relámpagos periódicos; los destellos se omiten con movimiento reducido y a velocidades de 10×/30×. Las gotas siguen el tiempo de reproducción y se detienen al pausar. Efectos locales de Three.js, sin descargas adicionales. Esta selección todavía no recalcula el tráfico ni representa efectos calibrados del clima.

## Camión y paneles de paso

El camión entra por el lateral libre antes de la avería, frena hasta la ubicación marcada y permanece detenido entre `t_inicio` y `t_fin`; después acelera y sale hacia el sur. Los conos aparecen mientras está varado. Es una trayectoria ilustrativa adicional, independiente de las llegadas del tráfico; no se cuenta como un vehículo más de la base.

Los paneles físicos junto a la vía alternan su indicador con ese mismo horario. El paso reducido se obtiene de `3600 / obstruccion.intervalo_paso_s` (12 s → máximo 300 veh/h). El normal indica ausencia de restricción adicional, sin inventar una capacidad calibrada. Los semáforos y colas pueden producir un flujo real inferior.

## Pantalla completa

Botón exterior «Pantalla completa» en cada vista. En ese modo los controles flotan: arrastrar la cabecera para moverlos (o usar flechas con el asa enfocada), «Ocultar» para plegarlos y «Mostrar» para recuperarlos. «Salir» o Escape devuelve la vista normal conservando la reproducción. Si el navegador no permite fullscreen nativo, se maximiza dentro de la ventana.

A la izquierda hay dos indicadores pequeños: gota para el nivel de lluvia y dial para la velocidad de reproducción. El panel aparece inicialmente a la derecha y se mantiene dentro de los bordes al arrastrar o redimensionar.
