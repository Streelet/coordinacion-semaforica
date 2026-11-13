import { useEffect } from 'react'
import { ESCENARIOS } from './config.js'
import { cargarTodo, reloj, useTienda } from './estado.js'
import Escena from './Escena.jsx'
import { Controles } from './Panel.jsx'

// Hace avanzar el reloj de la reproducción.
function useReloj() {
  useEffect(() => {
    let cuadro
    let anterior = performance.now()
    const paso = (ahora) => {
      const dt = Math.min((ahora - anterior) / 1000, 0.1)
      anterior = ahora
      const { reproduciendo, velocidad, set } = useTienda.getState()
      if (reproduciendo) {
        reloj.t += dt * velocidad
        if (reloj.t >= reloj.duracion) {
          reloj.t = reloj.duracion
          set({ reproduciendo: false })
        }
      }
      cuadro = requestAnimationFrame(paso)
    }
    cuadro = requestAnimationFrame(paso)
    return () => cancelAnimationFrame(cuadro)
  }, [])
}

export default function App() {
  const estado = useTienda((s) => s.estado)
  const mensaje = useTienda((s) => s.mensaje)
  const modo = useTienda((s) => s.modo)
  const escenarios = useTienda((s) => s.escenarios)

  useEffect(() => {
    cargarTodo()
  }, [])
  useReloj()

  if (estado === 'cargando') return <div className="aviso-central">Cargando la maqueta…</div>
  if (estado === 'error') return <div className="aviso-central error">{mensaje}</div>

  const visibles = modo === 'comparar' ? ESCENARIOS.map((e) => e.id) : [modo]
  const esDemo = Object.values(escenarios).some((e) => e.meta.es_demo)

  return (
    <div className="pagina">
      <header className="encabezado">
        <div>
          <h1>Séptima Avenida · W29–W30</h1>
          <p>Mismo tráfico y misma obstrucción; cambia solo la estrategia de semáforos.</p>
        </div>
        {esDemo && <span className="insignia-demo">Datos de demostración · no son resultados</span>}
      </header>
      <Controles />
      <main className={`rejilla rejilla-${visibles.length}`}>
        {visibles.map((id) => (
          <Escena key={id} escenario={escenarios[id]} />
        ))}
      </main>
    </div>
  )
}
