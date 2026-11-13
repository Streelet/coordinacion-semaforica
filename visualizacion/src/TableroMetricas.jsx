import { useMemo, useRef } from 'react'
import { Text } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { reloj } from './estado.js'
import { flujoReciente, metricaEn, regulando } from './trayectoria.js'

// Tablero físico en la manzana oeste del tramo. Solo lee métricas del motor; no calcula tráfico.
const FUENTE = import.meta.env.BASE_URL + 'fonts/Nunito-variable.ttf'
const TINTA = '#172033'
const SUAVE = '#475569'
const AZUL = '#2155eb'
const NARANJA = '#ea580c'
const ROJO = '#dc2626'
const VACIO = '#e2e8f0'
const miles = (n) => Math.round(n).toLocaleString('es-MX')

const ANCHO = 48
const ALTO = 60
const TILE = { w: 22.6, h: 25 }

function Baldosa({ x, y, titulo, acento, children }) {
  return (
    <group position={[x, y, 0]}>
      <mesh position={[0, 0, 0.55]}>
        <boxGeometry args={[TILE.w, TILE.h, 0.5]} />
        <meshBasicMaterial color="#f8fafc" />
      </mesh>
      <mesh position={[-TILE.w / 2 + 0.5, 0, 0.85]}>
        <boxGeometry args={[1, TILE.h - 1.4, 0.2]} />
        <meshBasicMaterial ref={acento} color={AZUL} />
      </mesh>
      <Text font={FUENTE} position={[-TILE.w / 2 + 2, TILE.h / 2 - 2.6, 0.9]} anchorX="left" fontSize={1.35} fontWeight={700} color={SUAVE} letterSpacing={0.01}>
        {titulo}
      </Text>
      {children}
    </group>
  )
}

export default function TableroMetricas({ escenario }) {
  const { metricas, regulacion, obstruccion, meta, red } = escenario
  const K = red.tramo.capacidad
  const almacen = meta.parametros?.almacen_cuadra_previa ?? K
  const carriles = 3

  const r = {
    ocup: useRef(), ocupSub: useRef(), cola: useRef(), colaSub: useRef(), verde: useRef(), verdeSub: useRef(),
    salidas: useRef(), salidasSub: useRef(), estado: useRef(), chip: useRef(),
    acOcup: useRef(), acCola: useRef(), acVerde: useRef(), acSal: useRef(), barraCola: useRef(),
  }
  const celdas = useRef([])
  const memo = useRef({})

  // Celdas 3D del tramo: 3 carriles × 11 lugares, se levantan cuando hay un carro.
  const posiciones = useMemo(() => {
    const out = []
    for (let i = 0; i < K; i++) {
      const fila = i % carriles
      const col = Math.floor(i / carriles)
      out.push([-9.2 + col * 1.72, -4.6 - fila * 2.1])
    }
    return out
  }, [K])

  const poner = (ref, clave, texto, color) => {
    const m = memo.current
    if (m[clave] === texto + color) return
    m[clave] = texto + color
    ref.current.text = texto
    if (color) ref.current.color = color
    ref.current.sync()
  }

  useFrame(() => {
    const t = reloj.t
    const n = metricaEn(metricas, 'ocupacion_tramo', t)
    const cola = metricaEn(metricas, 'cola_norte', t)
    const verde = metricaEn(metricas, 'verde_perdido', t)
    const verdeAntes = metricaEn(metricas, 'verde_perdido', Math.max(0, t - 10))
    const sal = metricaEn(metricas, 'salidas_tramo', t)
    const flujo = flujoReciente(metricas, t)
    const camion = t >= obstruccion.t_inicio && t < obstruccion.t_fin
    const regula = regulando(regulacion, t)

    const nivel = n >= K ? ROJO : n >= 0.8 * K ? NARANJA : AZUL
    poner(r.ocup, 'ocup', `${n} / ${K}`, nivel === AZUL ? TINTA : nivel)
    poner(r.ocupSub, 'ocupSub', n >= K ? 'Lleno: la cola toca W30' : `${K - n} lugares libres`, n >= K ? ROJO : SUAVE)
    r.acOcup.current.color.set(nivel)
    celdas.current.forEach((c, i) => {
      if (!c) return
      const lleno = i < n
      c.scale.z = lleno ? 1 : 0.25
      c.material.color.set(lleno ? nivel : VACIO)
    })

    const desborda = cola > almacen
    poner(r.cola, 'cola', `${cola} carros`, desborda ? ROJO : TINTA)
    poner(r.colaSub, 'colaSub', desborda ? '¡Llegó a W31!' : `Caben ${almacen} antes de W31`, desborda ? ROJO : SUAVE)
    r.acCola.current.color.set(desborda ? ROJO : cola > 0.7 * almacen ? NARANJA : AZUL)
    const frac = Math.min(cola / almacen, 1)
    r.barraCola.current.scale.x = Math.max(frac, 0.001)
    r.barraCola.current.position.x = -9.6 + (19.2 * frac) / 2
    r.barraCola.current.material.color.set(desborda ? ROJO : frac > 0.7 ? NARANJA : AZUL)

    const subiendo = verde > verdeAntes
    poner(r.verde, 'verde', `${miles(verde)} s`, subiendo ? NARANJA : TINTA)
    poner(r.verdeSub, 'verdeSub', subiendo ? 'Ahora: verde sin poder avanzar' : 'Verde en W30 sin lugar en el tramo', subiendo ? NARANJA : SUAVE)
    r.acVerde.current.color.set(subiendo ? NARANJA : AZUL)

    poner(r.salidas, 'sal', `${miles(sal)}`, TINTA)
    poner(r.salidasSub, 'salSub', flujo === null ? 'Ritmo: midiendo…' : `Ritmo: ${miles(flujo)} veh/h`, camion ? NARANJA : SUAVE)
    r.acSal.current.color.set(camion ? NARANJA : AZUL)

    const texto = camion && regula ? 'CAMIÓN · SENSOR REGULANDO' : camion ? 'CAMIÓN OBSTRUYENDO' : regula ? 'SENSOR REGULANDO' : 'TRÁFICO NORMAL'
    const color = camion ? NARANJA : regula ? '#f97316' : '#16a34a'
    poner(r.estado, 'estado', texto, '#ffffff')
    if (memo.current.chip !== color) {
      memo.current.chip = color
      r.chip.current.color.set(color)
    }
  })

  const fila1 = ALTO / 2 - 8 - TILE.h / 2
  const fila2 = fila1 - TILE.h - 1.2
  const col1 = -TILE.w / 2 - 0.6
  const col2 = TILE.w / 2 + 0.6

  return (
    <group position={[-40, 0.6, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      {/* base del tablero */}
      <mesh position={[0, 0, -0.3]}>
        <boxGeometry args={[ANCHO + 1.2, ALTO + 1.2, 1.2]} />
        <meshBasicMaterial color="#cbd5e1" />
      </mesh>
      <mesh position={[0, 0, 0.32]}>
        <planeGeometry args={[ANCHO, ALTO]} />
        <meshBasicMaterial color="#ffffff" />
      </mesh>
      <Text font={FUENTE} position={[-ANCHO / 2 + 1.6, ALTO / 2 - 3, 0.5]} anchorX="left" fontSize={3} fontWeight={800} color={TINTA}>
        {`TABLERO ${meta.estrategia}`}
      </Text>
      <mesh position={[ANCHO / 2 - 13.5, ALTO / 2 - 3, 0.45]}>
        <boxGeometry args={[25, 3.8, 0.3]} />
        <meshBasicMaterial ref={r.chip} color="#16a34a" />
      </mesh>
      <Text ref={r.estado} font={FUENTE} position={[ANCHO / 2 - 13.5, ALTO / 2 - 3, 0.7]} fontSize={1.8} fontWeight={700} color="#ffffff">
        TRÁFICO NORMAL
      </Text>

      <Baldosa x={col1} y={fila1} titulo="CARROS EN EL TRAMO" acento={r.acOcup}>
        <Text ref={r.ocup} font={FUENTE} position={[-TILE.w / 2 + 2, 5.6, 0.9]} anchorX="left" fontSize={4.8} fontWeight={800} color={TINTA}>{`0 / ${K}`}</Text>
        <Text ref={r.ocupSub} font={FUENTE} position={[-TILE.w / 2 + 2, 1.2, 0.9]} anchorX="left" fontSize={1.6} color={SUAVE} maxWidth={TILE.w - 3}> </Text>
        {posiciones.map(([x, y], i) => (
          <mesh key={i} ref={(m) => (celdas.current[i] = m)} position={[x, y, 1.1]}>
            <boxGeometry args={[1.4, 1.7, 1.2]} />
            <meshBasicMaterial color={VACIO} />
          </mesh>
        ))}
      </Baldosa>

      <Baldosa x={col2} y={fila1} titulo="FILA ANTES DE W30" acento={r.acCola}>
        <Text ref={r.cola} font={FUENTE} position={[-TILE.w / 2 + 2, 5.6, 0.9]} anchorX="left" fontSize={4.6} fontWeight={800} color={TINTA}>0 carros</Text>
        <Text ref={r.colaSub} font={FUENTE} position={[-TILE.w / 2 + 2, 1.2, 0.9]} anchorX="left" fontSize={1.6} color={SUAVE} maxWidth={TILE.w - 3}> </Text>
        <mesh position={[0, -6.5, 0.9]}>
          <boxGeometry args={[19.2, 2.4, 0.3]} />
          <meshBasicMaterial color={VACIO} />
        </mesh>
        <mesh ref={r.barraCola} position={[-9.6, -6.5, 1.15]}>
          <boxGeometry args={[19.2, 2.4, 0.6]} />
          <meshBasicMaterial color={AZUL} />
        </mesh>
        <Text font={FUENTE} position={[9.6, -9.3, 0.9]} anchorX="right" fontSize={1.3} color={SUAVE}>W31</Text>
      </Baldosa>

      <Baldosa x={col1} y={fila2} titulo="VERDE DESAPROVECHADO" acento={r.acVerde}>
        <Text ref={r.verde} font={FUENTE} position={[-TILE.w / 2 + 2, 2.6, 0.9]} anchorX="left" fontSize={4.8} fontWeight={800} color={TINTA}>0 s</Text>
        <Text ref={r.verdeSub} font={FUENTE} position={[-TILE.w / 2 + 2, -3.4, 0.9]} anchorX="left" fontSize={1.6} color={SUAVE} maxWidth={TILE.w - 3}> </Text>
      </Baldosa>

      <Baldosa x={col2} y={fila2} titulo="SALIERON DEL TRAMO" acento={r.acSal}>
        <Text ref={r.salidas} font={FUENTE} position={[-TILE.w / 2 + 2, 2.6, 0.9]} anchorX="left" fontSize={4.8} fontWeight={800} color={TINTA}>0</Text>
        <Text ref={r.salidasSub} font={FUENTE} position={[-TILE.w / 2 + 2, -3.4, 0.9]} anchorX="left" fontSize={1.6} color={SUAVE} maxWidth={TILE.w - 3}> </Text>
      </Baldosa>
    </group>
  )
}
