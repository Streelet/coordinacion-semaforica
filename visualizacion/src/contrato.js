import Ajv from 'ajv'
import esquema from '../../contratos/reproduccion.schema.json' with { type: 'json' }
import esquemaManifiesto from '../../contratos/manifiesto.schema.json' with { type: 'json' }

const ajv = new Ajv({ allErrors: false })
const estructura = ajv.compile(esquema)
const manifiesto = ajv.compile(esquemaManifiesto)
const exigir = (condicion, mensaje) => { if (!condicion) throw new Error(mensaje) }
function comprobarEstructura(validar, datos) {
  if (!validar(datos)) {
    const e = validar.errors[0]
    throw new Error(`Formato incompatible: ${e.instancePath || 'raíz'} ${e.message}`)
  }
}
function ordenada(tiempos, nombre) {
  exigir(tiempos.every((t, i) => i === 0 || t > tiempos[i - 1]), `${nombre}: tiempos no crecientes`)
}

export function validarManifiesto(datos) {
  comprobarEstructura(manifiesto, datos)
  exigir(new Set(datos.escenarios.map(e => e.id)).size === 3, 'Manifiesto: A, B y C deben aparecer una vez')
  return datos
}

export function validarCorrida(datos, estrategia) {
  comprobarEstructura(estructura, datos)
  exigir(!estrategia || datos.meta.estrategia === estrategia, 'La estrategia del archivo no coincide con el manifiesto')
  const ids = new Set()
  for (const v of datos.vehiculos) {
    exigir(!ids.has(v.id), `Vehículo duplicado: ${v.id}`)
    ids.add(v.id)
    exigir(Object.hasOwn(datos.red.rutas, v.ruta), `Ruta desconocida: ${v.ruta}`)
    ordenada(v.k.map(p => p[0]), `Vehículo ${v.id}`)
    exigir(v.k.every((p, i) => i === 0 || p[1] >= v.k[i - 1][1]), `Vehículo ${v.id}: distancia decreciente`)
  }
  for (const [nombre, puntos] of Object.entries(datos.red.rutas)) {
    exigir(puntos.every((p, i) => i === 0 || Math.hypot(p[0] - puntos[i - 1][0], p[1] - puntos[i - 1][1]) > 0), `Ruta ${nombre}: segmento de longitud cero`)
  }
  for (const l of datos.red.lineas_alto) {
    exigir(Object.hasOwn(datos.red.nodos, l.nodo) && Object.hasOwn(datos.semaforos, l.nodo), 'Línea de alto sin nodo o semáforo')
  }
  for (const [nodo, cambios] of Object.entries(datos.semaforos)) {
    exigir(cambios[0][0] === 0, `Semáforo ${nodo}: falta estado inicial`)
    ordenada(cambios.map(p => p[0]), `Semáforo ${nodo}`)
  }
  ordenada(datos.regulacion.map(p => p[0]), 'Regulación')
  const tiempos = datos.metricas.t
  ordenada(tiempos, 'Métricas')
  exigir(tiempos[0] === 0 && tiempos.at(-1) <= datos.meta.duracion, 'Métricas fuera del horizonte')
  for (const [nombre, valores] of Object.entries(datos.metricas)) {
    exigir(Array.isArray(valores) && valores.length === tiempos.length, `Métrica ${nombre}: longitud incompatible con t`)
  }
  const o = datos.obstruccion
  exigir(o.t_inicio <= o.t_fin && o.t_fin <= datos.meta.duracion, 'Horario de obstrucción inválido')
  return datos
}
