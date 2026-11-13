import { Component, Suspense, useMemo } from 'react'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import { COLORES, KENNEY, LARGO } from './config.js'
import { useTienda } from './estado.js'

// Todos los modelos miran hacia +Z (su "frente") y se apoyan en y = 0.
// Medidas en metros.

const OSCURO = '#5b5f6b'
const VIDRIO = '#eaf6fb'

function Rueda({ x, z, r = 0.38 }) {
  return (
    <mesh position={[x, r, z]} rotation={[0, 0, Math.PI / 2]}>
      <cylinderGeometry args={[r, r, 0.3, 10]} />
      <meshStandardMaterial color={OSCURO} />
    </mesh>
  )
}

export function AutoJuguete({ color }) {
  return (
    <group>
      <mesh position={[0, 0.72, 0]} castShadow>
        <boxGeometry args={[1.9, 0.75, 4.4]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[0, 1.35, -0.25]} castShadow>
        <boxGeometry args={[1.65, 0.6, 2.3]} />
        <meshStandardMaterial color={VIDRIO} />
      </mesh>
      <mesh position={[0, 1.68, -0.25]}>
        <boxGeometry args={[1.7, 0.12, 2.1]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <Rueda x={0.95} z={1.4} />
      <Rueda x={-0.95} z={1.4} />
      <Rueda x={0.95} z={-1.4} />
      <Rueda x={-0.95} z={-1.4} />
    </group>
  )
}

export function CamionJuguete({ color = COLORES.camion, largo = LARGO.camion }) {
  const caja = largo - 2.4
  return (
    <group>
      <mesh position={[0, 1.25, largo / 2 - 1.05]} castShadow>
        <boxGeometry args={[2.2, 1.7, 2.0]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[0, 1.75, largo / 2 - 0.3]}>
        <boxGeometry args={[1.9, 0.6, 0.55]} />
        <meshStandardMaterial color={VIDRIO} />
      </mesh>
      <mesh position={[0, 1.65, -largo / 2 + caja / 2 + 0.1]} castShadow>
        <boxGeometry args={[2.35, 2.5, caja]} />
        <meshStandardMaterial color="#fbf8f0" />
      </mesh>
      <Rueda x={1.1} z={largo / 2 - 1.1} r={0.5} />
      <Rueda x={-1.1} z={largo / 2 - 1.1} r={0.5} />
      <Rueda x={1.1} z={-largo / 2 + 1.3} r={0.5} />
      <Rueda x={-1.1} z={-largo / 2 + 1.3} r={0.5} />
    </group>
  )
}

export function BusJuguete({ color = COLORES.bus, largo = LARGO.bus }) {
  return (
    <group>
      <mesh position={[0, 1.6, 0]} castShadow>
        <boxGeometry args={[2.4, 2.4, largo - 0.3]} />
        <meshStandardMaterial color={color} />
      </mesh>
      <mesh position={[0, 2.0, 0]}>
        <boxGeometry args={[2.46, 0.8, largo - 1.2]} />
        <meshStandardMaterial color={VIDRIO} />
      </mesh>
      <Rueda x={1.15} z={largo / 2 - 1.8} r={0.5} />
      <Rueda x={-1.15} z={largo / 2 - 1.8} r={0.5} />
      <Rueda x={1.15} z={-largo / 2 + 1.8} r={0.5} />
      <Rueda x={-1.15} z={-largo / 2 + 1.8} r={0.5} />
    </group>
  )
}

export function ArbolJuguete({ variante = 0 }) {
  const copa = ['#8fcf8a', '#a6dc9a', '#7cc49a'][variante % 3]
  return (
    <group>
      <mesh position={[0, 1.4, 0]} castShadow>
        <cylinderGeometry args={[0.35, 0.45, 2.8, 8]} />
        <meshStandardMaterial color="#b98b62" />
      </mesh>
      {variante % 2 === 0 ? (
        <mesh position={[0, 4.4, 0]} castShadow>
          <icosahedronGeometry args={[2.6, 1]} />
          <meshStandardMaterial color={copa} flatShading />
        </mesh>
      ) : (
        <mesh position={[0, 5.0, 0]} castShadow>
          <coneGeometry args={[2.3, 5.2, 9]} />
          <meshStandardMaterial color={copa} flatShading />
        </mesh>
      )}
    </group>
  )
}

export function Cono() {
  return (
    <mesh position={[0, 0.5, 0]}>
      <coneGeometry args={[0.38, 1.0, 10]} />
      <meshStandardMaterial color="#f59a4a" />
    </mesh>
  )
}

// --- Modelos de Kenney (opcionales) ---

// Si un .glb no carga, se muestra el modelo de juguete en su lugar.
class Respaldo extends Component {
  constructor(props) {
    super(props)
    this.state = { fallo: false }
  }
  static getDerivedStateFromError() {
    return { fallo: true }
  }
  render() {
    return this.state.fallo ? this.props.alternativa : this.props.children
  }
}

// Carga un .glb, lo escala para que mida `largo` metros y lo apoya en el piso.
function ModeloGLB({ url, largo, vehiculo }) {
  const { scene } = useGLTF(url)
  const { objeto, escala, posicion, giro } = useMemo(() => {
    const copia = scene.clone(true)
    copia.traverse((o) => {
      if (o.isMesh) o.castShadow = true
    })
    const caja = new THREE.Box3().setFromObject(copia)
    const tam = caja.getSize(new THREE.Vector3())
    const centro = caja.getCenter(new THREE.Vector3())
    const k = largo / Math.max(tam.x, tam.z)
    return {
      objeto: copia,
      escala: k,
      posicion: [-centro.x * k, -caja.min.y * k, -centro.z * k],
      giro: (tam.x > tam.z ? Math.PI / 2 : 0) + (vehiculo && KENNEY.girar180 ? Math.PI : 0),
    }
  }, [scene, largo, vehiculo])
  return (
    <group rotation={[0, giro, 0]}>
      <primitive object={objeto} scale={escala} position={posicion} />
    </group>
  )
}

// Elige el modelo de Kenney si está disponible; si no, el de juguete.
export function Modelo({ clase, indice = 0, largo, children }) {
  const disponibles = useTienda((s) => s.modelos[clase])
  if (!disponibles || disponibles.length === 0) return children
  const url = disponibles[indice % disponibles.length]
  return (
    <Respaldo alternativa={children}>
      <Suspense fallback={children}>
        <ModeloGLB url={url} largo={largo} vehiculo={['auto', 'camion', 'bus', 'obstruccion'].includes(clase)} />
      </Suspense>
    </Respaldo>
  )
}

export function Vehiculo3D({ tipo, color, indice }) {
  if (tipo === 'camion') {
    return (
      <Modelo clase="camion" indice={indice} largo={LARGO.camion}>
        <CamionJuguete />
      </Modelo>
    )
  }
  if (tipo === 'bus') {
    return (
      <group rotation={[0, Math.PI, 0]}>
        <Modelo clase="bus" indice={indice} largo={LARGO.bus}>
          <BusJuguete />
        </Modelo>
      </group>
    )
  }
  return (
    <Modelo clase="auto" indice={indice} largo={LARGO.auto}>
      <AutoJuguete color={COLORES.autos[color % COLORES.autos.length]} />
    </Modelo>
  )
}
