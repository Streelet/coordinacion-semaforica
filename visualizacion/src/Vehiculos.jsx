import { useEffect, useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { LARGO } from './config.js'
import { reloj } from './estado.js'
import { Vehiculo3D } from './Modelos.jsx'
import { distanciaEnTiempo, posicionEnRuta } from './trayectoria.js'

// Un vehículo: en cada cuadro lee el reloj y se coloca donde dice el registro.
function Vehiculo({ v, ruta }) {
  const ref = useRef()
  const mitad = LARGO[v.tipo] / 2
  useFrame(() => {
    const g = ref.current
    if (!g) return
    const t = reloj.t
    if (t < v.t0 || t > v.t1) {
      g.visible = false
      return
    }
    // El registro guarda la posición del frente del vehículo; el modelo se centra medio largo atrás.
    const p = posicionEnRuta(ruta, distanciaEnTiempo(v.k, t) - mitad)
    g.visible = true
    g.position.set(p.x, 0, -p.y) // plano (x, y) → escena (x, 0, -y)
    g.rotation.y = Math.atan2(p.dx, -p.dy)
  })
  return (
    <group ref={ref} visible={false}>
      <Vehiculo3D tipo={v.tipo} color={v.color} indice={v.id} />
    </group>
  )
}

// Monta solo los vehículos que están en la escena cerca del instante actual.
export default function Vehiculos({ escenario }) {
  const [activos, setActivos] = useState([])
  const firma = useRef('')
  useEffect(() => {
    const revisar = () => {
      const t = reloj.t
      const lista = escenario.vehiculos.filter((v) => v.t0 <= t + 2 && v.t1 >= t - 1)
      const nueva = lista.map((v) => v.id).join(',')
      if (nueva !== firma.current) {
        firma.current = nueva
        setActivos(lista)
      }
    }
    revisar()
    const id = setInterval(revisar, 200)
    return () => clearInterval(id)
  }, [escenario])

  return activos.map((v) => <Vehiculo key={v.id} v={v} ruta={escenario.rutas[v.ruta]} />)
}
