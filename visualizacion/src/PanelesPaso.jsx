import { useRef } from 'react'
import { Text } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { reloj } from './estado.js'
import { capacidades, flujoReciente } from './trayectoria.js'

const FUENTE = import.meta.env.BASE_URL + 'fonts/Nunito-variable.ttf'
const miles = (n) => n.toLocaleString('es-MX')

// Letrero físico junto al tramo: capacidad del paso y lo que está pasando ahora (motor).
function PanelPaso({ escenario, reducido, capacidad, posicion }) {
  const obstruccion = escenario.obstruccion
  const borde = useRef()
  const piloto = useRef()
  const estado = useRef()
  const vivo = useRef()
  const anterior = useRef({ encendido: null, texto: null })
  const colorActivo = reducido ? '#ea580c' : '#2155eb'
  useFrame(() => {
    const t = reloj.t
    const averia = t >= obstruccion.t_inicio && t < obstruccion.t_fin
    const encendido = reducido ? averia : !averia
    const flujo = encendido ? flujoReciente(escenario.metricas, t) : null
    const texto = encendido ? (flujo === null ? 'Pasando: midiendo…' : `Pasando: ${miles(flujo)} veh/h`) : 'Pasando: —'
    const a = anterior.current
    if (encendido !== a.encendido) {
      a.encendido = encendido
      const color = encendido ? colorActivo : '#94a3b8'
      borde.current.color.set(color)
      piloto.current.color.set(color)
      estado.current.text = encendido ? 'ACTIVO' : 'INACTIVO'
      estado.current.color = encendido ? colorActivo : '#64748b'
      estado.current.sync()
      vivo.current.color = encendido ? '#172033' : '#94a3b8'
    }
    if (texto !== a.texto) {
      a.texto = texto
      vivo.current.text = texto
      vivo.current.sync()
    }
  })
  return (
    <group position={posicion} rotation={[-Math.PI / 2, 0, 0]}>
      <mesh>
        <boxGeometry args={[42, 25, 0.6]} />
        <meshBasicMaterial ref={borde} color="#94a3b8" />
      </mesh>
      <mesh position={[0, 0, 0.34]}>
        <planeGeometry args={[40.5, 23.5]} />
        <meshBasicMaterial color="#ffffff" />
      </mesh>
      <mesh position={[16.8, 8.5, 0.4]}>
        <circleGeometry args={[1.2, 20]} />
        <meshBasicMaterial ref={piloto} color="#94a3b8" />
      </mesh>
      <Text font={FUENTE} position={[-17, 8.4, 0.45]} anchorX="left" fontSize={2.6} fontWeight={800} color="#172033">
        {reducido ? 'PASO REDUCIDO · 1 carril' : 'PASO NORMAL · 3 carriles'}
      </Text>
      <Text font={FUENTE} position={[-17, 3.2, 0.45]} anchorX="left" fontSize={2.5} color="#334155">
        {capacidad ? `Capacidad ≈ ${miles(capacidad)} veh/h` : 'Capacidad sin especificar'}
      </Text>
      <Text ref={vivo} font={FUENTE} position={[-17, -2.6, 0.45]} anchorX="left" fontSize={3.6} fontWeight={800} color="#94a3b8">
        Pasando: —
      </Text>
      <Text ref={estado} font={FUENTE} position={[0, -8.3, 0.45]} fontSize={2.6} color="#64748b">
        INACTIVO
      </Text>
    </group>
  )
}

export default function PanelesPaso({ escenario }) {
  const cap = capacidades(escenario)
  return (
    <group>
      <PanelPaso escenario={escenario} reducido={false} capacidad={cap.normal} posicion={[40, 0.6, -14]} />
      <PanelPaso escenario={escenario} reducido capacidad={cap.reducida} posicion={[40, 0.6, 14]} />
    </group>
  )
}
