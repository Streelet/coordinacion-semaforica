import { create } from 'zustand'
import { FUENTE_CORRIDAS, KENNEY } from './config.js'
import { cargarCorridas } from './fuenteCorridas.js'

// El reloj vive fuera de React: cambia 60 veces por segundo y cada objeto
// de la escena lo lee directamente, sin volver a dibujar la interfaz.
export const reloj = { t: 0, duracion: 1 }

export const useTienda = create((set) => ({
  estado: 'cargando', // 'cargando' | 'listo' | 'error'
  mensaje: '',
  escenarios: {},
  modelos: {}, // archivos de Kenney encontrados, por clase
  clima: 'sin', // ambiente visual común; no recalcula el tráfico
  modo: 'comparar', // 'comparar' | 'A' | 'B' | 'C'
  reproduciendo: true,
  velocidad: 4,
  set,
}))

const url = (ruta) => import.meta.env.BASE_URL + ruta

async function existe(archivo) {
  try {
    const r = await fetch(url(archivo), { method: 'HEAD' })
    const tipo = r.headers.get('content-type') || ''
    return r.ok && !tipo.includes('text/html')
  } catch {
    return false
  }
}

async function detectarModelos() {
  const modelos = {}
  for (const [clase, archivos] of Object.entries(KENNEY.archivos)) {
    const encontrados = []
    for (const a of archivos) {
      if (await existe(KENNEY.carpeta + a)) encontrados.push(url(KENNEY.carpeta + a))
    }
    modelos[clase] = encontrados
  }
  return modelos
}

export async function cargarTodo() {
  const { set } = useTienda.getState()
  try {
    const base = new URL(import.meta.env.BASE_URL, window.location.href)
    const escenarios = await cargarCorridas(new URL(FUENTE_CORRIDAS, base))
    reloj.duracion = Math.max(...Object.values(escenarios).map((e) => e.meta.duracion))
    reloj.t = 0
    const modelos = await detectarModelos()
    set({ escenarios, modelos, estado: 'listo' })
  } catch (error) {
    set({ estado: 'error', mensaje: String(error.message || error) })
  }
}
