import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { Calles, Entorno } from './Entorno.jsx'
import { Indicadores } from './Panel.jsx'
import { Obstruccion, Semaforos, Sensor } from './Semaforos.jsx'
import Vehiculos from './Vehiculos.jsx'
import Clima from './Clima.jsx'
import PanelesPaso from './PanelesPaso.jsx'
import ControlesFlotantes from './ControlesFlotantes.jsx'
import IndicadoresVisuales from './IndicadoresVisuales.jsx'

// Encuadre del corredor central; los controles comparten el mismo objetivo.
function EncuadrarCamara({ controles }) {
  const camera = useThree((s) => s.camera)
  const size = useThree((s) => s.size)
  useLayoutEffect(() => {
    camera.position.set(60, 260, 160)
    camera.zoom = Math.min(size.width / 180, size.height / 180)
    camera.lookAt(0, 0, 0)
    camera.updateProjectionMatrix()
    if (controles.current) {
      controles.current.target.set(0, 0, 0)
      controles.current.update()
    }
  }, [camera, size.width, size.height, controles])
  return null
}

export default function Escena({ escenario }) {
  const controles = useRef()
  const visor = useRef()
  const botonAmpliar = useRef()
  const nativo = useRef(false)
  const [ampliada, setAmpliada] = useState(false)

  const cerrar = async () => {
    if (document.fullscreenElement === visor.current) await document.exitFullscreen()
    setAmpliada(false)
    botonAmpliar.current?.focus()
  }
  const ampliar = async () => {
    setAmpliada(true)
    try {
      if (document.fullscreenEnabled) await visor.current.requestFullscreen()
    } catch {
      // Se conserva la vista maximizada en la ventana si el navegador rechaza Fullscreen.
    }
  }

  useEffect(() => {
    const cambio = () => {
      if (document.fullscreenElement === visor.current) nativo.current = true
      else if (nativo.current) {
        nativo.current = false
        setAmpliada(false)
        botonAmpliar.current?.focus()
      }
    }
    document.addEventListener('fullscreenchange', cambio)
    return () => document.removeEventListener('fullscreenchange', cambio)
  }, [])

  useEffect(() => {
    if (!ampliada) return
    const anterior = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    visor.current.querySelector('button')?.focus()
    const escape = (e) => {
      if (e.key === 'Escape' && !document.fullscreenElement) {
        setAmpliada(false)
        botonAmpliar.current?.focus()
      }
    }
    document.addEventListener('keydown', escape)
    return () => {
      document.body.style.overflow = anterior
      document.removeEventListener('keydown', escape)
    }
  }, [ampliada])

  const mantenerFoco = (e) => {
    if (!ampliada || e.key !== 'Tab') return
    const botones = [...visor.current.querySelectorAll('button, input')]
    const primero = botones[0]
    const ultimo = botones[botones.length - 1]
    if (e.shiftKey && document.activeElement === primero) { e.preventDefault(); ultimo.focus() }
    else if (!e.shiftKey && document.activeElement === ultimo) { e.preventDefault(); primero.focus() }
  }
  return (
    <section className="panel" data-estrategia={escenario.meta.estrategia}>
      <div className="cabecera-vista">
        <span>Vista {escenario.meta.estrategia}</span>
        <button ref={botonAmpliar} className="boton chico" onClick={ampliar}
          aria-label={`Pantalla completa ${escenario.meta.estrategia}`}>⛶ Pantalla completa</button>
      </div>
      <div ref={visor} className={`visor ${ampliada ? 'ampliado' : ''}`}
        role={ampliada ? 'dialog' : undefined} aria-modal={ampliada || undefined}
        aria-label={`Vista 3D de la estrategia ${escenario.meta.estrategia}`} onKeyDown={mantenerFoco}>
      <div className="vista-3d">
      <Canvas flat shadows orthographic dpr={[1, 2]} camera={{ position: [60, 260, 160], zoom: 2, near: 0.1, far: 1000 }}>
        <color attach="background" args={['#ffffff']} />
        <EncuadrarCamara controles={controles} />
        <Clima />
        <Calles red={escenario.red} />
        <Entorno red={escenario.red} />
        <Sensor escenario={escenario} />
        <Semaforos escenario={escenario} />
        <Obstruccion escenario={escenario} />
        <PanelesPaso escenario={escenario} />
        <Vehiculos escenario={escenario} />
        <OrbitControls ref={controles} makeDefault enableDamping={false} maxPolarAngle={1.05} minZoom={0.6} maxZoom={14} />
      </Canvas>
      </div>
      {ampliada && <>
        <IndicadoresVisuales />
        <ControlesFlotantes estrategia={escenario.meta.estrategia} salir={cerrar} />
      </>}
      </div>
      <Indicadores escenario={escenario} />
    </section>
  )
}
