import { useEffect, useState } from 'react'
import { ESCENARIOS, VELOCIDADES } from './config.js'
import { reloj, useTienda } from './estado.js'
import { metricaEn, regulando } from './trayectoria.js'

// Lee el reloj unas 8 veces por segundo para actualizar textos y barras.
export function useTiempo(ms = 120) {
  const [t, setT] = useState(reloj.t)
  useEffect(() => {
    const id = setInterval(() => setT(reloj.t), ms)
    return () => clearInterval(id)
  }, [ms])
  return t
}

function mmss(t) {
  const s = Math.max(0, Math.floor(t))
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
}

export function Controles({ seleccionarEscenario = true }) {
  const t = useTiempo()
  const clima = useTienda((s) => s.clima)
  const modo = useTienda((s) => s.modo)
  const reproduciendo = useTienda((s) => s.reproduciendo)
  const velocidad = useTienda((s) => s.velocidad)
  const set = useTienda((s) => s.set)

  const alternar = () => {
    if (!reproduciendo && reloj.t >= reloj.duracion) reloj.t = 0
    set({ reproduciendo: !reproduciendo })
  }

  return (
    <>
    <section className="controles">
      <button className="boton principal" onClick={alternar}>
        {reproduciendo ? 'Pausar' : 'Reproducir'}
      </button>
      <button
        className="boton"
        onClick={() => {
          reloj.t = 0
        }}
      >
        Reiniciar
      </button>
      <div className="grupo">
        {VELOCIDADES.map((v) => (
          <button key={v} className={`boton chico ${v === velocidad ? 'activo' : ''}`} onClick={() => set({ velocidad: v })}>
            ×{v}
          </button>
        ))}
      </div>
      <input
        className="deslizador"
        type="range"
        min="0"
        max={reloj.duracion}
        step="1"
        value={Math.floor(t)}
        onChange={(e) => {
          reloj.t = Number(e.target.value)
        }}
        aria-label="Tiempo de la simulación"
      />
      <span className="tiempo">
        {mmss(t)} / {mmss(reloj.duracion)}
      </span>
      {seleccionarEscenario && <div className="grupo">
        <button className={`boton chico ${modo === 'comparar' ? 'activo' : ''}`} onClick={() => set({ modo: 'comparar' })}>
          Comparar
        </button>
        {ESCENARIOS.map((e) => (
          <button key={e.id} className={`boton chico ${modo === e.id ? 'activo' : ''}`} onClick={() => set({ modo: e.id })}>
            {e.id}
          </button>
        ))}
      </div>}
    </section>
    <section className="controles-clima" aria-label="Ambiente visual">
      <span className="rotulo-clima">Ambiente visual</span>
      <div className="grupo" role="group" aria-label="Intensidad de lluvia">
        {[['sin', 'Sin lluvia'], ['ligera', 'Lluvia ligera'], ['intensa', 'Lluvia intensa']].map(([valor, nombre]) => (
          <button key={valor} className={`boton chico ${clima === valor ? 'activo' : ''}`}
            aria-pressed={clima === valor} onClick={() => set({ clima: valor })}>
            {nombre}
          </button>
        ))}
      </div>
      <span className="nota-clima">Efecto visual · el tráfico de la demo no se recalcula.</span>
    </section>
    </>
  )
}

// Tarjeta con los indicadores de un escenario en el instante actual.
export function Indicadores({ escenario }) {
  const t = useTiempo()
  const { meta, metricas, resumen, red, obstruccion, regulacion } = escenario
  const capacidad = red.tramo.capacidad
  const ocupacion = metricaEn(metricas, 'ocupacion_tramo', t)
  const llego = resumen.t_cola_llega_w30 !== null && t >= resumen.t_cola_llega_w30
  const hayCamion = t >= obstruccion.t_inicio && t < obstruccion.t_fin
  const regula = regulando(regulacion, t)

  return (
    <div className="indicadores" aria-label={`Indicadores de la estrategia ${meta.estrategia}`}>
      <div className="titulo-escenario">
        <span className="letra">{meta.estrategia}</span>
        <span>{meta.nombre}</span>
      </div>
      <div className="fila">
        <span>Carros en el tramo</span>
        <strong>
          {ocupacion} de {capacidad}
        </strong>
      </div>
      <div className="barra">
        <div className={`relleno ${ocupacion >= capacidad - 3 ? 'alto' : ''}`} style={{ width: `${Math.min(100, (100 * ocupacion) / capacidad)}%` }} />
      </div>
      <div className="fila">
        <span>¿La cola llegó a W30?</span>
        <strong className={llego ? 'mal' : 'bien'}>{llego ? `Sí, a los ${mmss(resumen.t_cola_llega_w30)}` : 'Todavía no'}</strong>
      </div>
      <div className="fila">
        <span>Verde desaprovechado en W30</span>
        <strong>{Math.round(metricaEn(metricas, 'verde_perdido', t))} s</strong>
      </div>
      <div className="fila">
        <span>Salieron por el tramo</span>
        <strong>{metricaEn(metricas, 'salidas_tramo', t)}</strong>
      </div>
      <div className="etiquetas">
        {hayCamion && <span className="etiqueta camion">Camión obstruyendo</span>}
        {regula && <span className="etiqueta regula">Regulando el ingreso</span>}
      </div>
    </div>
  )
}
