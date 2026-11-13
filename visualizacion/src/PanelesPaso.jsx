import { useRef } from 'react'
import { Text } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { reloj } from './estado.js'

const FUENTE = import.meta.env.BASE_URL + 'fonts/Nunito-variable.ttf'

// Señalización física al costado de la vía, solicitada para explicar el paso.
function PanelPaso({ obstruccion, reducido, valor, posicion }) {
  const borde = useRef()
  const piloto = useRef()
  const activo = useRef()
  const inactivo = useRef()
  const anterior = useRef(null)
  useFrame(() => {
    const averia = reloj.t >= obstruccion.t_inicio && reloj.t < obstruccion.t_fin
    const encendido = reducido ? averia : !averia
    if (encendido === anterior.current) return
    anterior.current = encendido
    const color = encendido ? (reducido ? '#ea580c' : '#2155eb') : '#94a3b8'
    borde.current.color.set(color)
    piloto.current.color.set(color)
    activo.current.visible = encendido
    inactivo.current.visible = !encendido
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
      <Text font={FUENTE} position={[-17, 8, 0.45]} anchorX="left" fontSize={2.7} color="#172033">
        {reducido ? 'PASO REDUCIDO' : 'PASO NORMAL'}
      </Text>
      <Text font={FUENTE} position={[0, 1, 0.45]} fontSize={reducido ? 4.6 : 2.8} color="#172033" maxWidth={36} textAlign="center">
        {valor}
      </Text>
      <Text ref={activo} font={FUENTE} position={[0, -7.7, 0.45]} fontSize={2.6} color={reducido ? '#c2410c' : '#2155eb'} visible={false}>
        ACTIVO
      </Text>
      <Text ref={inactivo} font={FUENTE} position={[0, -7.7, 0.45]} fontSize={2.6} color="#64748b">
        INACTIVO
      </Text>
    </group>
  )
}

export default function PanelesPaso({ escenario }) {
  const o = escenario.obstruccion
  const intervalo = o.intervalo_paso_s
  const valor = intervalo > 0 ? `≤ ${Math.round(3600 / intervalo)} veh/h` : 'Sin especificar'
  return (
    <group>
      <PanelPaso obstruccion={o} reducido={false} valor={'Sin restricción\nadicional'} posicion={[40, 0.6, -14]} />
      <PanelPaso obstruccion={o} reducido valor={valor} posicion={[40, 0.6, 14]} />
    </group>
  )
}
