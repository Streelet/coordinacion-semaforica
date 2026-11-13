// Configuración de la visualización. Es lo único que hay que tocar para
// cambiar de los datos de demostración a los resultados reales de SimPy.

// Único punto de conexión: manifiesto publicado por el exportador del motor.
export const FUENTE_CORRIDAS = 'datos/manifest.json'
export const ESCENARIOS = [{ id: 'A' }, { id: 'B' }, { id: 'C' }]

export const VELOCIDADES = [1, 4, 10, 30]

// Colores de la maqueta
export const COLORES = {
  pasto: '#ffffff',
  acera: '#e2e8f0',
  asfalto: '#475569',
  marca: '#ffffff',
  autos: ['#2563eb', '#e11d48', '#059669', '#f59e0b', '#7c3aed', '#0891b2'],
  camion: '#2563eb',
  bus: '#f59e0b',
  edificios: ['#94a3b8', '#64748b', '#cbd5e1', '#475569'],
  luz: { V: '#00b86b', A: '#ffb000', R: '#ee2849' },
}

export const LARGO = { auto: 4.5, camion: 7.5, bus: 10 }

// Selección local de los cuatro paquetes Kenney (CC0).
export const KENNEY = {
  carpeta: 'modelos/',
  girar180: false,
  archivos: {
    auto: ['car/sedan.glb', 'car/hatchback-sports.glb', 'car/suv.glb', 'car/taxi.glb', 'car/sedan-sports.glb', 'car/suv-luxury.glb'],
    camion: ['car/truck.glb'],
    bus: [], // El Car Kit no incluye autobús: conservamos el modelo de la plantilla.
    obstruccion: ['car/delivery.glb'],
    arbol: ['nature/tree_default.glb', 'nature/tree_oak.glb', 'nature/tree_detailed.glb'],
    edificio: ['city/building-a.glb', 'city/building-b.glb', 'city/building-c.glb', 'city/building-d.glb'],
    cono: ['roads/construction-cone.glb'],
    farola: ['roads/light-square.glb'],
  },
}
