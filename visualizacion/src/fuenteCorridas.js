import { validarCorrida, validarManifiesto } from './contrato.js'
import { prepararRuta } from './trayectoria.js'
import { COLORES } from './config.js'

// Adaptador de lectura: no ejecuta reglas de tráfico ni escribe resultados.
export async function cargarCorridas(manifiestoUrl, obtener = fetch) {
  const leer = async (url) => {
    const respuesta = await obtener(url)
    if (!respuesta.ok) throw new Error(`No se pudo leer ${url} (HTTP ${respuesta.status})`)
    return respuesta.json()
  }
  const manifiesto = validarManifiesto(await leer(manifiestoUrl))
  const lista = await Promise.all(manifiesto.escenarios.map(async (e) => {
    const url = new URL(e.archivo, manifiestoUrl)
    try {
      return validarCorrida(await leer(url), e.id)
    } catch (error) {
      throw new Error(`${e.id} (${e.archivo}): ${error.message}`)
    }
  }))
  const referencia = lista[0]
  for (const datos of lista) {
    for (const campo of ['entradas_id', 'replica_id', 'duracion']) {
      if (datos.meta[campo] !== referencia.meta[campo]) throw new Error(`Corridas incompatibles: ${campo} difiere entre estrategias`)
    }
    if (JSON.stringify(datos.red) !== JSON.stringify(referencia.red)) throw new Error('Corridas incompatibles: la red difiere entre estrategias')
  }
  return Object.fromEntries(lista.map((datos) => {
    const rutas = Object.fromEntries(Object.entries(datos.red.rutas).map(([id, puntos]) => [id, prepararRuta(puntos, datos.red.radio_giro ?? 6)]))
    const vehiculos = datos.vehiculos.map(v => ({ ...v, color: v.color ?? v.id % COLORES.autos.length, t0: v.k[0][0], t1: v.k.at(-1)[0] }))
    return [datos.meta.estrategia, { ...datos, rutas, vehiculos }]
  }))
}
