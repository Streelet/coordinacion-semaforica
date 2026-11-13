import { useMemo } from 'react'
import { COLORES } from './config.js'
import { ArbolJuguete, Modelo } from './Modelos.jsx'

const BORDE = 138 // la maqueta va de -138 a +138 m

// Generador pseudoaleatorio con semilla: la maqueta sale igual cada vez.
function azar(semilla) {
  let a = semilla
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

const esVertical = (c) => c.de[0] === c.a[0]

// Piso, aceras, asfalto y pasos peatonales. Todo en metros reales.
export function Calles({ red }) {
  const cruces = Object.values(red.nodos)
  return (
    <group>
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[2 * BORDE + 60, 2 * BORDE + 60]} />
        <meshStandardMaterial color={COLORES.pasto} />
      </mesh>
      {red.calles.map((c) => {
        const v = esVertical(c)
        const largo = 2 * BORDE
        const centro = v ? [c.de[0], 0, 0] : [0, 0, -c.de[1]]
        return (
          <group key={c.nombre} position={centro}>
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]} receiveShadow>
              <planeGeometry args={v ? [c.ancho + 12, largo] : [largo, c.ancho + 12]} />
              <meshStandardMaterial color={COLORES.acera} />
            </mesh>
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.04, 0]} receiveShadow>
              <planeGeometry args={v ? [c.ancho, largo] : [largo, c.ancho]} />
              <meshStandardMaterial color={COLORES.asfalto} />
            </mesh>
          </group>
        )
      })}
      {/* pasos peatonales en los cuatro lados de cada cruce */}
      {cruces.map(([nx, ny], n) =>
        [
          [0, 6.2, true],
          [0, -6.2, true],
          [6.2, 0, false],
          [-6.2, 0, false],
        ].map(([dx, dy, aLoAncho], lado) =>
          [-3, -1.5, 0, 1.5, 3].map((d) => (
            <mesh
              key={`${n}-${lado}-${d}`}
              rotation={[-Math.PI / 2, 0, 0]}
              position={[nx + dx + (aLoAncho ? d : 0), 0.05, -(ny + dy + (aLoAncho ? 0 : d))]}
            >
              <planeGeometry args={aLoAncho ? [0.7, 2.0] : [2.0, 0.7]} />
              <meshStandardMaterial color={COLORES.marca} />
            </mesh>
          )),
        ),
      )}
    </group>
  )
}

// Árboles en las aceras y edificios bajitos en las manzanas.
export function Entorno({ red }) {
  const { arboles, edificios } = useMemo(() => {
    const r = azar(7)
    const cruces = Object.values(red.nodos)
    const lejosDeCalles = (x, y, margen) =>
      red.calles.every((c) => (esVertical(c) ? Math.abs(x - c.de[0]) : Math.abs(y - c.de[1])) > c.ancho / 2 + margen)
    const arboles = []
    for (const c of red.calles) {
      const v = esVertical(c)
      for (const lado of [-1, 1]) {
        for (let d = -BORDE + 8; d <= BORDE - 8; d += 13) {
          const fuera = c.ancho / 2 + 4.3
          const x = v ? c.de[0] + lado * fuera : d + (r() - 0.5) * 3
          const y = v ? d + (r() - 0.5) * 3 : c.de[1] + lado * fuera
          const cercaDeCruce = cruces.some(([nx, ny]) => Math.hypot(x - nx, y - ny) < 16)
          const sobreOtraCalle = !red.calles.every((o) => o === c || (esVertical(o) ? Math.abs(x - o.de[0]) : Math.abs(y - o.de[1])) > o.ancho / 2 + 3)
          if (!cercaDeCruce && !sobreOtraCalle) arboles.push({ x, y, variante: Math.floor(r() * 3), escala: 0.62 + r() * 0.2 })
        }
      }
    }
    const edificios = []
    for (let x = -118; x <= 118; x += 26) {
      for (let y = -118; y <= 118; y += 24) {
        // Espacio reservado para los dos paneles de capacidad junto al tramo.
        if (x > 15 && x < 68 && Math.abs(y) < 33) continue
        // Espacio reservado para el tablero de métricas al oeste del tramo.
        if (x < -12 && x > -70 && Math.abs(y) < 36) continue
        if (!lejosDeCalles(x, y, 19) || r() < 0.18) continue
        edificios.push({
          x: x + (r() - 0.5) * 4,
          y: y + (r() - 0.5) * 4,
          ancho: 13 + r() * 6,
          fondo: 12 + r() * 6,
          alto: 4 + r() * 5,
          color: COLORES.edificios[Math.floor(r() * COLORES.edificios.length)],
        })
      }
    }
    return { arboles, edificios }
  }, [red])

  return (
    <group>
      {arboles.map((a, i) => (
        <group key={`a${i}`} position={[a.x, 0, -a.y]} scale={a.escala}>
          <Modelo clase="arbol" indice={a.variante} largo={5.5}>
            <ArbolJuguete variante={a.variante} />
          </Modelo>
        </group>
      ))}
      {[-105, -65, 0, 65, 105].map((y) => (
        <group key={`l${y}`} position={[-11, 0, -y]}>
          <Modelo clase="farola" largo={3} />
        </group>
      ))}
      {edificios.map((e, i) => (
        <group key={`e${i}`} position={[e.x, 0, -e.y]}>
          <Modelo clase="edificio" indice={i} largo={Math.max(e.ancho, e.fondo)}>
          <mesh position={[0, e.alto / 2, 0]} castShadow receiveShadow>
            <boxGeometry args={[e.ancho, e.alto, e.fondo]} />
            <meshStandardMaterial color={e.color} />
          </mesh>
          <mesh position={[0, e.alto + 0.25, 0]}>
            <boxGeometry args={[e.ancho - 2, 0.5, e.fondo - 2]} />
            <meshStandardMaterial color="#fbf8f0" />
          </mesh>
          </Modelo>
        </group>
      ))}
    </group>
  )
}
