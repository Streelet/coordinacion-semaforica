import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { validarCorrida } from '../src/contrato.js'
import { cargarCorridas } from '../src/fuenteCorridas.js'
import { metricaEn } from '../src/trayectoria.js'

const leer = nombre => JSON.parse(readFileSync(new URL(`../../contratos/${nombre}`, import.meta.url)))
const ejemplo = leer('ejemplo_A.json')

test('mismos casos válidos e inválidos que el exportador Python', () => {
  validarCorrida(ejemplo, 'A')
  for (const caso of leer('casos_invalidos.json')) {
    const datos = structuredClone(ejemplo)
    let destino = datos
    for (const campo of caso.ruta.slice(0, -1)) destino = destino[campo]
    destino[caso.ruta.at(-1)] = caso.valor
    assert.throws(() => validarCorrida(datos), undefined, caso.nombre)
  }
})

test('las métricas usan sus tiempos exportados y no anticipan muestras', () => {
  assert.equal(metricaEn(ejemplo.metricas, 'ocupacion_tramo', 9), 0)
  assert.equal(metricaEn(ejemplo.metricas, 'ocupacion_tramo', 10), 1)
  assert.equal(metricaEn(ejemplo.metricas, 'ocupacion_tramo', 200), 1)
})

test('carga A/B/C por manifiesto, sin mutar entradas; rechaza mezclar réplicas', async () => {
  const url = new URL('http://localhost/datos/manifest.json')
  const archivos = Object.fromEntries('ABC'.split('').map(id => {
    const datos = structuredClone(ejemplo)
    datos.meta.estrategia = id
    return [`${id}.json`, datos]
  }))
  const manifiesto = { version_contrato: '1.0', escenarios: 'ABC'.split('').map(id => ({id, archivo:`${id}.json`})) }
  const obtener = async url => ({ ok:true, json:async () => url.pathname.endsWith('manifest.json') ? manifiesto : archivos[url.pathname.split('/').at(-1)] })
  const copia = structuredClone(archivos)
  const resultado = await cargarCorridas(url, obtener)
  assert.equal(resultado.B.vehiculos[0].t0, 0)
  assert.deepEqual(archivos, copia)
  archivos['C.json'].meta.replica_id = 2
  await assert.rejects(cargarCorridas(url, obtener), /replica_id/)
})
