import { useEffect, useMemo, useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { Line } from '@react-three/drei'
import { reloj, useTienda } from './estado.js'

function useMovimientoReducido() {
  const [reducido, setReducido] = useState(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches)
  useEffect(() => {
    const consulta = window.matchMedia('(prefers-reduced-motion: reduce)')
    const actualizar = () => setReducido(consulta.matches)
    consulta.addEventListener('change', actualizar)
    return () => consulta.removeEventListener('change', actualizar)
  }, [])
  return reducido
}

// Distribución fija para que A, B y C compartan la misma lluvia visual.
function Gotas({ intensa, reducido, tiempo }) {
  const geometria = useRef()
  const cantidad = intensa ? 3200 : 1500
  const { origen, posiciones } = useMemo(() => {
    let semilla = 19
    const azar = () => {
      semilla = (Math.imul(semilla, 1664525) + 1013904223) >>> 0
      return semilla / 4294967296
    }
    const origen = new Float32Array(cantidad * 3)
    const posiciones = new Float32Array(cantidad * 6)
    for (let i = 0; i < cantidad; i++) {
      origen[i * 3] = azar() * 320 - 160
      origen[i * 3 + 1] = azar() * 95
      origen[i * 3 + 2] = azar() * 320 - 160
    }
    return { origen, posiciones }
  }, [cantidad])

  useFrame(() => {
    const t = reducido ? 0 : tiempo.current
    const velocidad = intensa ? 42 : 26
    const largo = intensa ? 5 : 3.3
    for (let i = 0; i < cantidad; i++) {
      const x = ((origen[i * 3] + 160 + t * 2) % 320) - 160
      const y = ((origen[i * 3 + 1] - t * velocidad) % 95 + 95) % 95
      const z = origen[i * 3 + 2]
      const k = i * 6
      posiciones[k] = x
      posiciones[k + 1] = y
      posiciones[k + 2] = z
      posiciones[k + 3] = x - largo * 0.12
      posiciones[k + 4] = y + largo
      posiciones[k + 5] = z
    }
    geometria.current.attributes.position.needsUpdate = true
  })

  return (
    <lineSegments frustumCulled={false} raycast={() => null}>
      <bufferGeometry ref={geometria}>
        <bufferAttribute attach="attributes-position" args={[posiciones, 3]} />
      </bufferGeometry>
      <lineBasicMaterial color={intensa ? '#1d4ed8' : '#2563eb'} transparent opacity={intensa ? 0.8 : 0.7} depthWrite={false} />
    </lineSegments>
  )
}

export default function Clima() {
  const nivel = useTienda((s) => s.clima)
  const reducido = useMovimientoReducido()
  const tiempo = useRef(0)
  const luz = useRef()
  const rayo = useRef()
  const intensa = nivel === 'intensa'
  const puntosRayo = useMemo(() => [
    -48, 83, -25, -52, 71, -25,
    -52, 71, -25, -47, 73, -25,
    -47, 73, -25, -55, 57, -25,
    -55, 57, -25, -51, 59, -25,
    -51, 59, -25, -60, 43, -25,
    -52, 71, -25, -61, 65, -25,
    -61, 65, -25, -63, 58, -25,
  ], [])

  useFrame((_, delta) => {
    // Sigue el reloj de reproducción: pausa, reinicio y velocidades comunes.
    tiempo.current = reloj.t
    const fase = reloj.t % 14
    // Un pulso suave cada 14 s simulados; desactivado a velocidades de 10× y 30×.
    const habilitado = intensa && !reducido && useTienda.getState().velocidad <= 4
    const destello = habilitado && fase >= 7 && fase < 8.2 ? Math.sin((fase - 7) / 1.2 * Math.PI) : 0
    const objetivo = (nivel === 'sin' ? 1.5 : intensa ? 0.8 : 1.15) + destello * 1.25
    luz.current.intensity += (objetivo - luz.current.intensity) * Math.min(delta * 7, 1)
    rayo.current.visible = destello > 0.05
    rayo.current.material.opacity = destello * 0.8
  })

  return (
    <>
      <hemisphereLight args={['#ffffff', '#cbd5e1', intensa ? 0.85 : 1.25]} />
      <directionalLight
        ref={luz} position={[-60, 140, 50]} intensity={1.5} castShadow
        shadow-mapSize={[2048, 2048]} shadow-camera-left={-180}
        shadow-camera-right={180} shadow-camera-top={180}
        shadow-camera-bottom={-180} shadow-camera-far={500} shadow-bias={-0.0005}
      />
      {nivel !== 'sin' && <Gotas intensa={intensa} reducido={reducido} tiempo={tiempo} />}
      <Line ref={rayo} points={puntosRayo} segments lineWidth={2.5}
        color="#568bff" transparent opacity={0} depthWrite={false} visible={false} raycast={() => null} />
    </>
  )
}
