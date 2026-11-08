"""Última consulta histórica, acotada a los dos emplazamientos y tres referencias cercanas."""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from auditoria_historicos import cargar_token, guardar, OBJETIVO, LION

HISTORICO = 'btm5-ppia'
PRIMARIA = '7ym2-wayt'
W23 = {33639: 'Seventh W23–W24, entrada SB',
       32830: 'W23 Sixth–Seventh, entrada WB',
       33638: 'W23 Seventh–Eighth, entrada EB',
       33637: 'Seventh W22–W23, salida SB'}
REFERENCIAS = {33652: 'Seventh W27–W28, SB',
               33891: 'W29 Fifth–Broadway, WB',
               34013: 'W30 Fifth–Broadway, EB'}
IDS = sorted(set(OBJETIVO) | set(W23) | set(REFERENCIAS))


def obtener_complemento(root, actualizar=False):
    root = Path(root)
    out = root / 'resultados' / 'auditoria_historico_complementario'
    out.mkdir(parents=True, exist_ok=True)
    required = ['esquema', 'esquema_primaria', 'global', 'inventario', 'conteos',
                'resumen_ids', 'conteos_referencia', 'primaria', 'lion_correspondencia', 'lion_accesos', 'consultas', 'manifest']
    if not actualizar and all((out / f'{name}.json').exists() for name in required):
        return out
    token = cargar_token(root)
    (out / 'manifest.json').unlink(missing_ok=True)
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 502, 503, 504],
                  allowed_methods=['GET', 'POST'], respect_retry_after_header=True)
    session.mount('https://', HTTPAdapter(max_retries=retry))
    log = []

    def get_json(url, params=None):
        response = session.get(url, params=params, timeout=180)
        if not response.ok:
            raise RuntimeError(f'HTTP {response.status_code} consultando metadatos públicos.')
        result = response.json()
        if isinstance(result, dict) and result.get('error'):
            raise RuntimeError('El servicio rechazó la consulta geográfica.')
        return result

    def query(name, dataset, sql):
        rows, page = [], 1
        while True:
            payload = {'query': sql, 'page': {'pageNumber': page, 'pageSize': 1000},
                       'includeSynthetic': False}
            response = session.post(f'https://data.cityofnewyork.us/api/v3/views/{dataset}/query.json',
                                    json=payload, headers={'X-App-Token': token}, timeout=240)
            if not response.ok:
                raise RuntimeError(f'HTTP {response.status_code} en consulta {name}, página {page}.')
            batch = response.json()
            if not isinstance(batch, list):
                raise RuntimeError('Formato SODA inesperado.')
            log.append({'nombre': name, 'dataset': dataset, **payload, 'filas': len(batch)})
            rows.extend(batch)
            if len(batch) < 1000:
                break
            page += 1
            if page > 20:
                raise RuntimeError('Se alcanzó el límite preventivo de descarga.')
        guardar(out / f'{name}.json', rows)
        return rows

    for dataset, name in [(HISTORICO, 'esquema'), (PRIMARIA, 'esquema_primaria')]:
        guardar(out / f'{name}.json', get_json(f'https://data.cityofnewyork.us/api/views/{dataset}.json'))
    query('global', HISTORICO, 'SELECT count(*) AS n, min(date) AS inicio, max(date) AS fin')
    inventory = query('inventario', HISTORICO,
        "SELECT segmentid, roadway_name, `from`, `to`, direction, count(*) AS n, min(date) AS inicio, max(date) AS fin "
        "WHERE upper(roadway_name) LIKE '%7%' OR upper(roadway_name) LIKE '%SEVENTH%' "
        "OR upper(roadway_name) LIKE '%29%' OR upper(roadway_name) LIKE '%30%' OR upper(roadway_name) LIKE '%23%' "
        "GROUP BY segmentid, roadway_name, `from`, `to`, direction ORDER BY segmentid")
    order = 'ORDER BY segmentid,date,direction,id,:id'
    original_ids = sorted(set(OBJETIVO) | {33639, 32830, 33638})
    query('conteos', HISTORICO, f"SELECT * WHERE segmentid IN ({','.join(map(str,original_ids))}) {order}")
    where = f"segmentid IN ({','.join(map(str,IDS))})"
    query('resumen_ids', HISTORICO, f'SELECT segmentid,roadway_name,`from`,`to`,direction,count(*) AS n,min(date) AS inicio,max(date) AS fin WHERE {where} GROUP BY segmentid,roadway_name,`from`,`to`,direction ORDER BY segmentid,inicio')
    query('conteos_referencia', HISTORICO, f'SELECT * WHERE {where} {order}')
    query('primaria', PRIMARIA, f'SELECT * WHERE {where} ORDER BY segmentid,requestid,yr,m,d,hh,mm,direction,:id')
    all_ids = sorted({int(row['segmentid']) for row in inventory if row.get('segmentid')} | set(IDS))
    params = {'f': 'json', 'where': 'SegmentID IN (' + ','.join("'%07d'" % sid for sid in all_ids) + ')',
              'outFields': 'SegmentID,Street,NodeIDFrom,NodeIDTo,TrafDir,XFrom,YFrom,XTo,YTo,LBoro,RBoro',
              'outSR': 2263, 'returnGeometry': 'true', 'resultRecordCount': 2000}
    geometry = get_json(LION + '/query', params)
    if geometry.get('exceededTransferLimit'):
        raise RuntimeError('Geometrías truncadas: no aceptar correspondencia incompleta.')
    guardar(out / 'lion_correspondencia.json', geometry)
    guardar(out / 'lion_correspondencia.consulta.json', params)
    nodes = "'0021334','0021335','0021247'"
    params = {'f': 'json', 'where': f"FeatureTyp = '0' AND (NodeIDFrom IN ({nodes}) OR NodeIDTo IN ({nodes}))",
              'outFields': 'SegmentID,Street,NodeIDFrom,NodeIDTo,TrafDir,XFrom,YFrom,XTo,YTo,LBoro,RBoro',
              'returnGeometry': 'true', 'outSR': 2263, 'resultRecordCount': 2000}
    accesses = get_json(LION + '/query', params)
    if accesses.get('exceededTransferLimit'):
        raise RuntimeError('Accesos truncados en LION.')
    discovered = {int(f['attributes']['SegmentID']) for f in accesses['features']}
    if not discovered.issubset(set(IDS)):
        raise RuntimeError('LION identifica otros accesos: revisar selección antes de concluir.')
    guardar(out / 'lion_accesos.json', accesses)
    guardar(out / 'lion_accesos.consulta.json', params)
    guardar(out / 'consultas.json', log)
    guardar(out / 'manifest.json', {
        'fecha_consulta': datetime.now(ZoneInfo('America/Guatemala')).isoformat(),
        'datasets': [HISTORICO, PRIMARIA], 'ids_consultados': IDS,
        'nota': 'Dos fuentes separadas. No se mezclan años ni campañas; App Token solo en encabezados.',
    })
    return out
