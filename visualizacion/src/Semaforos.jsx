import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { COLORES } from './config.js'
import { reloj } from './estado.js'
import { CamionJuguete, Cono, Modelo } from './Modelos.jsx'
import { estadoSemaforo, regulando } from './trayectoria.js'

// Línea de alto pintada del color de la luz + poste con una esfera grande.
// Así el estado se lee de un vistazo desde arriba.
function Luz({ linea, cambios, ancho }) {
  const franja = useRef()
  const foco = useRef()
  useFrame(() => {
    const estado = estadoSemaforo(cambios, reloj.t)[linea.fase]
    const color = COLORES.luz[estado]
    if (franja.current) {
      franja.current.color.set(color)
      franja.current.emissive.set(color)
    }
    if (foco.current) {
      foco.current.color.set(color)
      foco.current.emissive.set(color)
    }
  })
  const enX = linea.a_lo_largo === 'x'
  const lado = ancho / 2 + 1.6
  // el poste va a un lado de la calle, junto a la línea de alto
  const poste = enX ? [linea.x - lado, 0, -linea.y] : [linea.x, 0, -(linea.y - lado)]
  return (
    <group>
      <mesh position={[linea.x, 0.06, -linea.y]}>
        <boxGeometry args={enX ? [ancho - 1, 0.08, 1.3] : [1.3, 0.08, ancho - 1]} />
        <meshStandardMaterial ref={franja} emissiveIntensity={0.55} />
      </mesh>
      <group position={poste}>
        <mesh position={[0, 3, 0]} castShadow>
          <cylinderGeometry args={[0.22, 0.28, 6, 8]} />
          <meshStandardMaterial color="#6f7480" />
        </mesh>
        <mesh position={[0, 6.6, 0]}>
          <sphereGeometry args={[1.25, 16, 12]} />
          <meshStandardMaterial ref={foco} emissiveIntensity={0.7} />
        </mesh>
      </group>
    </group>
  )
}

export function Semaforos({ escenario }) {
  const { red, semaforos } = escenario
  const anchoDe = (linea) => {
    // la línea cruza la calle por la que llegan los carros de esa fase
    const vertical = red.calles.find((c) => c.de[0] === c.a[0])
    const horizontal = red.calles.find((c) => c.de[1] === c.a[1] && c.de[1] === red.nodos[linea.nodo][1])
    return (linea.fase === 'av' ? vertical : horizontal).ancho
  }
  return red.lineas_alto.map((l, i) => <Luz key={i} linea={l} cambios={semaforos[l.nodo]} ancho={anchoDe(l)} />)
}

// Zona del sensor de la estrategia C: cambia de color mientras regula.
export function Sensor({ escenario }) {
  const material = useRef()
  const { tramo } = escenario.red
  useFrame(() => {
    if (material.current) material.current.color.set(regulando(escenario.regulacion, reloj.t) ? '#f97316' : '#2563eb')
  })
  if (escenario.meta.estrategia !== 'C') return null
  const largo = Math.abs(tramo.de[1] - tramo.a[1])
  return (
    <mesh position={[tramo.de[0], 0.05, -(tramo.de[1] + tramo.a[1]) / 2]} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[9.6, largo]} />
      <meshBasicMaterial ref={material} transparent opacity={0.28} />
    </mesh>
  )
}

// Llega por su carril, se atraviesa sobre los carriles bloqueados y luego sale.
// La restricción (paso reducido) solo rige mientras está varado.
export function Obstruccion({ escenario }) {
  const grupo = useRef()
  const conos = useRef()
  const o = escenario.obstruccion
  const angulo = ((o.angulo ?? 0) * Math.PI) / 180
  const avenida = escenario.red.calles.find((c) => c.de[0] === c.a[0])
  const norte = Math.max(avenida.de[1], avenida.a[1])
  const sur = Math.min(avenida.de[1], avenida.a[1])
  const velocidad = escenario.meta.parametros.velocidad_libre
  const distanciaEntrada = norte - o.y
  const distanciaSalida = o.y - sur
  const GIRO = 2.5 // s para atravesarse o enderezarse
  const duracionEntrada = distanciaEntrada / velocidad + 2
  const tEntrada = o.t_inicio - duracionEntrada - GIRO
  const duracionSalida = distanciaSalida / velocidad + 1
  useFrame(() => {
    const t = reloj.t
    grupo.current.visible = t >= tEntrada && t < o.t_fin + GIRO + duracionSalida
    conos.current.visible = t >= o.t_inicio && t < o.t_fin
    let y = o.y
    let giro = 0
    if (t < o.t_inicio - GIRO) {
      const transcurrido = Math.max(0, t - tEntrada)
      const frenando = Math.max(0, transcurrido - (duracionEntrada - 4))
      const recorrido = velocidad * transcurrido - velocidad / 8 * frenando ** 2
      y = norte - Math.min(distanciaEntrada, recorrido)
    } else if (t < o.t_fin) {
      giro = Math.min(1, (t - (o.t_inicio - GIRO)) / GIRO)
    } else if (t < o.t_fin + GIRO) {
      giro = 1 - (t - o.t_fin) / GIRO
    } else {
      const transcurrido = t - o.t_fin - GIRO
      const recorrido = transcurrido < 2 ? velocidad / 4 * transcurrido ** 2 : velocidad * (transcurrido - 1)
      y = o.y - recorrido
    }
    grupo.current.position.set(o.x + o.lado, 0, -y)
    grupo.current.rotation.y = angulo * giro
  })
  // Conos antes del camión, cerrando los carriles bloqueados (coordenadas del plano).
  const xs = [-4.3, -2.6, -0.9, 0.8]
  return (
    <>
      <group ref={grupo} visible={false}>
        <Modelo clase="obstruccion" largo={7.5}>
          <CamionJuguete color="#ea580c" />
        </Modelo>
      </group>
      <group ref={conos} visible={false}>
        {xs.map((x, i) => (
          <group key={x} position={[o.x + x, 0, -(o.y + 6.5 - i * 0.6)]}>
            <Modelo clase="cono" largo={0.8}><Cono /></Modelo>
          </group>
        ))}
      </group>
    </>
  )
}
