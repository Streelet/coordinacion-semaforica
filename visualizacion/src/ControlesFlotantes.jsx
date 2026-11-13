import { useLayoutEffect, useRef, useState } from 'react'
import { Controles } from './Panel.jsx'
import IndicadoresVisuales from './IndicadoresVisuales.jsx'

export default function ControlesFlotantes({ estrategia, salir }) {
  const panel = useRef()
  const arrastre = useRef(null)
  const [ocultos, setOcultos] = useState(false)
  const [posicion, setPosicion] = useState(() => ({ x: Math.max(8, window.innerWidth - 440), y: 20 }))

  const limitar = ({ x, y }) => {
    const caja = panel.current.getBoundingClientRect()
    const contenedor = panel.current.parentElement.getBoundingClientRect()
    return {
      x: Math.max(8, Math.min(x, contenedor.width - caja.width - 8)),
      y: Math.max(8, Math.min(y, contenedor.height - caja.height - 8)),
    }
  }

  useLayoutEffect(() => {
    const ajustar = () => setPosicion((p) => limitar(p))
    const observador = new ResizeObserver(ajustar)
    observador.observe(panel.current)
    window.addEventListener('resize', ajustar)
    return () => {
      observador.disconnect()
      window.removeEventListener('resize', ajustar)
    }
  }, [])

  const iniciar = (e) => {
    if (!e.isPrimary || e.button !== 0) return
    e.currentTarget.setPointerCapture(e.pointerId)
    arrastre.current = { id: e.pointerId, x: e.clientX, y: e.clientY, origen: posicion }
  }
  const mover = (e) => {
    const a = arrastre.current
    if (!a || a.id !== e.pointerId) return
    setPosicion(limitar({ x: a.origen.x + e.clientX - a.x, y: a.origen.y + e.clientY - a.y }))
  }
  const teclado = (e) => {
    const pasos = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }
    if (!pasos[e.key]) return
    e.preventDefault()
    const [x, y] = pasos[e.key]
    const paso = e.shiftKey ? 30 : 10
    setPosicion((p) => limitar({ x: p.x + x * paso, y: p.y + y * paso }))
  }

  return (
    <aside ref={panel} className={`controles-flotantes ${ocultos ? 'plegados' : ''}`}
      aria-label={`Controles flotantes de ${estrategia}`}
      style={{ transform: `translate3d(${posicion.x}px, ${posicion.y}px, 0)` }}>
      <div className="cabecera-flotante">
        <button className="agarre" aria-label={`Mover controles de ${estrategia}`}
          title="Arrastra para mover; también puedes usar las flechas del teclado"
          onPointerDown={iniciar} onPointerMove={mover} onPointerUp={() => { arrastre.current = null }}
          onPointerCancel={() => { arrastre.current = null }} onLostPointerCapture={() => { arrastre.current = null }}
          onKeyDown={teclado}>
          ⠿ Controles · {estrategia}
        </button>
        <button className="boton chico" aria-expanded={!ocultos} onClick={() => setOcultos(!ocultos)}>
          {ocultos ? 'Mostrar' : 'Ocultar'}
        </button>
        <button className="boton chico" onClick={salir}>Salir</button>
      </div>
      <IndicadoresVisuales enLinea />
      {!ocultos && <div className="cuerpo-flotante"><Controles seleccionarEscenario={false} /></div>}
    </aside>
  )
}
