"""Frontera de salida del motor: JSON versionado, sin dependencias de React/Three.js."""
import json
import math
import os
import tempfile
from pathlib import Path

from jsonschema import Draft7Validator

CONTRATOS = Path(__file__).resolve().parent.parent / 'contratos'
VERSION = '1.0'
UNIDADES = {'tiempo': 's', 'distancia': 'm', 'plano': 'x_este_y_norte', 'posicion_vehiculo': 'frente'}


def _estructura(datos, nombre):
    esquema = json.loads((CONTRATOS / nombre).read_text(encoding='utf-8'))
    error = next(Draft7Validator(esquema).iter_errors(datos), None)
    if error:
        ruta = '.'.join(map(str, error.absolute_path)) or 'raíz'
        raise ValueError(f'{ruta}: {error.message}')


def validar_corrida(datos):
    """Rechaza estructura, referencias o series incompatibles con el reproductor."""
    # También rechaza NaN/Infinity, que no son números JSON válidos.
    json.dumps(datos, allow_nan=False)
    _estructura(datos, 'reproduccion.schema.json')

    def comprobar(condicion, mensaje):
        if not condicion:
            raise ValueError(mensaje)

    def ordenada(tiempos, nombre):
        comprobar(all(a < b for a, b in zip(tiempos, tiempos[1:])), f'{nombre}: tiempos no crecientes')

    red = datos['red']
    ids = set()
    for v in datos['vehiculos']:
        comprobar(v['id'] not in ids, f'vehiculos: id repetido {v["id"]}')
        ids.add(v['id'])
        comprobar(v['ruta'] in red['rutas'], f'vehiculos.{v["id"]}: ruta desconocida')
        ordenada([p[0] for p in v['k']], f'vehiculos.{v["id"]}')
        comprobar(all(a[1] <= b[1] for a, b in zip(v['k'], v['k'][1:])), f'vehiculos.{v["id"]}: distancia decreciente')
    for nombre, puntos in red['rutas'].items():
        comprobar(all(math.dist(a, b) > 0 for a, b in zip(puntos, puntos[1:])), f'red.rutas.{nombre}: segmento de longitud cero')
    for linea in red['lineas_alto']:
        comprobar(linea['nodo'] in red['nodos'] and linea['nodo'] in datos['semaforos'], 'lineas_alto: nodo sin geometría o semáforo')
    for nodo, cambios in datos['semaforos'].items():
        comprobar(cambios[0][0] == 0, f'semaforos.{nodo}: falta estado inicial en t=0')
        ordenada([p[0] for p in cambios], f'semaforos.{nodo}')
    ordenada([p[0] for p in datos['regulacion']], 'regulacion')
    tiempos = datos['metricas']['t']
    ordenada(tiempos, 'metricas.t')
    comprobar(tiempos[0] == 0 and tiempos[-1] <= datos['meta']['duracion'], 'metricas.t: horizonte inválido')
    for nombre, valores in datos['metricas'].items():
        comprobar(isinstance(valores, list) and len(valores) == len(tiempos), f'metricas.{nombre}: longitud incompatible con t')
    o = datos['obstruccion']
    comprobar(o['t_inicio'] <= o['t_fin'] <= datos['meta']['duracion'], 'obstruccion: horario inválido')
    return datos


def _guardar(datos, destino):
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    contenido = json.dumps(datos, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destino.parent, delete=False) as f:
            temporal = f.name
            f.write(contenido)
        os.replace(temporal, destino)
    finally:
        if temporal and os.path.exists(temporal):
            os.unlink(temporal)
    return destino


def exportar_corrida(datos, destino, *, motor, entradas_id, replica_id=1):
    """El motor entrega su registro; esta función valida y escribe una copia."""
    registro = {**datos, 'version_contrato': VERSION, 'unidades': dict(UNIDADES), 'meta': {**datos['meta'], 'motor': motor, 'entradas_id': entradas_id, 'replica_id': replica_id}}
    validar_corrida(registro)
    return _guardar(registro, destino)


def exportar_manifiesto(escenarios, destino):
    """Publicar al final, una vez exportadas las tres corridas A/B/C."""
    datos = {'version_contrato': VERSION, 'escenarios': escenarios}
    _estructura(datos, 'manifiesto.schema.json')
    if {e['id'] for e in escenarios} != {'A', 'B', 'C'}:
        raise ValueError('manifiesto: debe incluir A, B y C sin repetir')
    return _guardar(datos, destino)
