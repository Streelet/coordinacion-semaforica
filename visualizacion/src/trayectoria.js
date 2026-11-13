// Funciones puras para leer el registro de la simulación.
// No simulan nada: solo interpolan lo que ya calculó el modelo en Python.

// Búsqueda binaria: índice del último elemento cuyo tiempo (posición 0) es <= t.
function indiceEn(lista, t) {
  let a = 0
  let b = lista.length - 1
  if (b < 0 || t < lista[0][0]) return -1
  while (a < b) {
    const m = (a + b + 1) >> 1
    if (lista[m][0] <= t) a = m
    else b = m - 1
  }
  return a
}

// Distancia recorrida en la ruta (m) en el instante t, según los puntos clave [t, s].
export function distanciaEnTiempo(k, t) {
  const i = indiceEn(k, t)
  if (i < 0) return k[0][1]
  if (i >= k.length - 1) return k[k.length - 1][1]
  const [t0, s0] = k[i]
  const [t1, s1] = k[i + 1]
  return s0 + ((s1 - s0) * (t - t0)) / (t1 - t0)
}

// Prepara una ruta (lista de puntos [x, y]) con sus distancias acumuladas.
export function prepararRuta(puntos, radio) {
  const acum = [0]
  for (let i = 1; i < puntos.length; i++) {
    acum.push(acum[i - 1] + Math.hypot(puntos[i][0] - puntos[i - 1][0], puntos[i][1] - puntos[i - 1][1]))
  }
  return { puntos, acum, radio, largo: acum[acum.length - 1] }
}

function puntoEnSegmento(ruta, i, d) {
  // punto a distancia d (desde el inicio de la ruta) dentro del segmento i → i+1
  const [x0, y0] = ruta.puntos[i]
  const [x1, y1] = ruta.puntos[i + 1]
  const u = (d - ruta.acum[i]) / (ruta.acum[i + 1] - ruta.acum[i])
  return [x0 + (x1 - x0) * u, y0 + (y1 - y0) * u]
}

// Posición y dirección en el plano a la distancia s de la ruta.
// En las esquinas redondea el giro con una curva suave de radio `ruta.radio`.
export function posicionEnRuta(ruta, s) {
  const { puntos, acum, radio } = ruta
  const d = Math.min(Math.max(s, 0), ruta.largo)
  for (let i = 1; i < puntos.length - 1; i++) {
    if (Math.abs(d - acum[i]) < radio) {
      const p0 = puntoEnSegmento(ruta, i - 1, acum[i] - radio)
      const p1 = puntos[i]
      const p2 = puntoEnSegmento(ruta, i, acum[i] + radio)
      const u = (d - (acum[i] - radio)) / (2 * radio)
      const v = 1 - u
      return {
        x: v * v * p0[0] + 2 * v * u * p1[0] + u * u * p2[0],
        y: v * v * p0[1] + 2 * v * u * p1[1] + u * u * p2[1],
        dx: 2 * v * (p1[0] - p0[0]) + 2 * u * (p2[0] - p1[0]),
        dy: 2 * v * (p1[1] - p0[1]) + 2 * u * (p2[1] - p1[1]),
      }
    }
  }
  let i = 0
  while (i < puntos.length - 2 && d > acum[i + 1]) i++
  const [x, y] = puntoEnSegmento(ruta, i, d)
  return { x, y, dx: puntos[i + 1][0] - puntos[i][0], dy: puntos[i + 1][1] - puntos[i][1] }
}

// Estado de un semáforo en t: { av, tr } con 'V', 'A' o 'R'.
export function estadoSemaforo(cambios, t) {
  const i = Math.max(indiceEn(cambios, t), 0)
  return { av: cambios[i][1], tr: cambios[i][2] }
}

// ¿Está activa la regulación (estrategia C) en t?
export function regulando(cambios, t) {
  const i = indiceEn(cambios, t)
  return i >= 0 && cambios[i][1] === 1
}

// Última muestra disponible: admite muestreo irregular y evita anticipar resultados.
export function metricaEn(metricas, nombre, t) {
  const tiempos = metricas.t
  let a = 0
  let b = tiempos.length
  while (a < b) {
    const m = (a + b) >> 1
    if (tiempos[m] <= t) a = m + 1
    else b = m
  }
  return metricas[nombre][Math.max(0, a - 1)]
}

// Ritmo de salida del tramo (veh/h) en la última `ventana` de segundos, a partir de las salidas acumuladas.
export function flujoReciente(metricas, t, ventana = 60) {
  const desde = Math.max(0, t - ventana)
  const n = metricaEn(metricas, 'salidas_tramo', t) - metricaEn(metricas, 'salidas_tramo', desde)
  const lapso = Math.max(t - desde, 1)
  return lapso < 15 ? null : Math.round((n * 3600) / lapso)
}

// Capacidad media del tramo (veh/h) en paso normal y reducido; la declara el motor en meta.parametros.
export function capacidades(escenario) {
  const p = escenario.meta.parametros ?? {}
  const reducida = p.capacidad_reducida_vph ?? (escenario.obstruccion.intervalo_paso_s > 0 ? 3600 / escenario.obstruccion.intervalo_paso_s : null)
  return { normal: p.capacidad_normal_vph ?? null, reducida }
}
