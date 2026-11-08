"""Consultas acotadas y caché local para auditar el corredor; nunca registra credenciales."""
import json
import math
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = 'https://data.cityofnewyork.us'
ENDPOINT = f'{BASE}/api/v3/views/7ym2-wayt/query.json'
LION = 'https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/ArcGIS/rest/services/LION/FeatureServer/0'
OBJETIVO = {
    33804: '7 Av, W30–W31: entrada sur a W30',
    33803: 'W30, 8–7 Av: entrada este a W30',
    33802: '7 Av, W29–W30: tramo central / entrada sur a W29',
    33894: 'W29, 6–7 Av: entrada oeste a W29',
    33800: '7 Av, W28–W29: salida sur de W29',
    33801: 'W29, 7–8 Av: salida oeste de W29',
    33896: 'W30, 7–6 Av: salida este de W30',
}
CENTRO = (986277, 211852)  # Punto medio de los nodos LION 21334 y 21335.
RADIO_M = 915


def punto(wkt):
    match = re.fullmatch(r'POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)', str(wkt))
    return tuple(map(float, match.groups())) if match else (math.nan, math.nan)


def distancia_m(wkt):
    x, y = punto(wkt)
    return math.hypot(x - CENTRO[0], y - CENTRO[1]) * 0.3048006096


def guardar(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def cargar_token(root):
    # Solo se carga el App Token; el Secret Token no interviene en lecturas públicas.
    token = ''
    for line in (root / '.env').read_text(encoding='utf-8').splitlines():
        key, sep, value = line.partition('=')
        if sep and key.strip() == 'SOCRATA_APP_TOKEN':
            token = value.strip().strip('\"\'')
    if not token:
        raise RuntimeError('Completa SOCRATA_APP_TOKEN en el archivo .env local.')
    return token


def obtener_evidencia(root, actualizar=False):
    """Reutiliza una auditoría completa o consulta solo agregados y los IDs cercanos."""
    root = Path(root)
    out = root / 'resultados' / 'auditoria_historicos'
    out.mkdir(parents=True, exist_ok=True)
    required = ['esquema', 'global', 'inventario_nombres', 'inventario_manhattan',
                'lion_zona', 'lion_esquema', 'lion_item', 'lion_cercanos', 'lion_nodos_alternativas', 'cercanos', 'resumen_ids', 'conteos', 'manifest']
    if not actualizar and all((out / f'{name}.json').exists() for name in required):
        return out
    token = cargar_token(root)
    (out / 'manifest.json').unlink(missing_ok=True)  # Una actualización fallida no constituye una caché completa.
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 502, 503, 504],
                  allowed_methods=['GET', 'POST'], respect_retry_after_header=True)
    session.mount('https://', HTTPAdapter(max_retries=retry))
    log = []

    def get_json(url, params=None):
        response = session.get(url, params=params, timeout=180)
        if not response.ok:
            raise RuntimeError(f'HTTP {response.status_code}; consulta pública fallida.')
        data = response.json()
        if isinstance(data, dict) and 'error' in data:
            raise RuntimeError('El servicio geográfico rechazó la consulta.')
        return data

    def query(name, sql, paginar=False):
        rows, page = [], 1
        size = 1000 if paginar else 10000
        while True:
            payload = {'query': sql, 'page': {'pageNumber': page, 'pageSize': size},
                       'includeSynthetic': False}
            response = session.post(ENDPOINT, json=payload,
                                    headers={'X-App-Token': token}, timeout=240)
            if not response.ok:
                raise RuntimeError(f'HTTP {response.status_code}; consulta {name}, página {page}.')
            batch = response.json()
            if not isinstance(batch, list):
                raise RuntimeError('Formato SODA inesperado.')
            log.append({'nombre': name, **payload, 'filas': len(batch)})
            rows.extend(batch)
            if len(batch) < size:
                break
            if not paginar:
                raise RuntimeError('Inventario posiblemente truncado; ampliar paginación.')
            page += 1
            if page > 80:
                raise RuntimeError('Se alcanzó el límite preventivo de descarga.')
        guardar(out / f'{name}.json', rows)
        return rows

    schema = get_json(f'{BASE}/api/views/7ym2-wayt.json')
    guardar(out / 'esquema.json', schema)
    query('global', 'SELECT boro, count(*) AS n, min(yr) AS primer_ano, max(yr) AS ultimo_ano GROUP BY boro')
    projection = ('segmentid, street, fromst, tost, direction, wktgeom, count(*) AS n, '
                  'min(yr) AS primer_ano, max(yr) AS ultimo_ano')
    group = 'segmentid, street, fromst, tost, direction, wktgeom'
    variants = "(upper(street) LIKE '%7%' OR upper(street) LIKE '%SEVENTH%' OR upper(street) LIKE '%29%' OR upper(street) LIKE '%30%')"
    query('inventario_nombres', f"SELECT {projection} WHERE upper(boro) = 'MANHATTAN' AND {variants} GROUP BY {group} ORDER BY street, segmentid")
    inventory = query('inventario_manhattan', f"SELECT {projection} WHERE upper(boro) = 'MANHATTAN' GROUP BY {group} ORDER BY segmentid")
    nearby = [dict(row, distancia_m=round(distancia_m(row.get('wktgeom')), 1))
              for row in inventory if distancia_m(row.get('wktgeom')) <= RADIO_M]
    guardar(out / 'cercanos.json', nearby)
    guardar(out / 'lion_esquema.json', get_json(LION, {'f': 'json'}))
    guardar(out / 'lion_item.json', get_json('https://www.arcgis.com/sharing/rest/content/items/db6fdacfc5ff44e7a244e2f798d98a7d', {'f': 'json'}))
    lion_params = {
        'f': 'json', 'where': "Street IN ('7 AVENUE','WEST 29 STREET','WEST 30 STREET','WEST 31 STREET','WEST 28 STREET','WEST 26 STREET','WEST 23 STREET','8 AVENUE','AVENUE OF THE AMERICAS')",
        'geometry': '985000,210000,988500,213500', 'geometryType': 'esriGeometryEnvelope',
        'inSR': 2263, 'outSR': 2263, 'spatialRel': 'esriSpatialRelIntersects',
        'outFields': 'SegmentID,Street,NodeIDFrom,NodeIDTo,TrafDir,XFrom,YFrom,XTo,YTo,Number_Travel_Lanes,StreetWidth_Min',
        'returnGeometry': 'true', 'resultRecordCount': 2000,
    }
    lion = get_json(LION + '/query', lion_params)
    if lion.get('exceededTransferLimit'):
        raise RuntimeError('Respuesta LION truncada.')
    guardar(out / 'lion_zona.json', lion)
    guardar(out / 'lion_zona.consulta.json', lion_params)
    ids = sorted(set(OBJETIVO) | {int(row['segmentid']) for row in nearby})
    nearby_ids = sorted({int(row['segmentid']) for row in nearby})
    p = {'f': 'json', 'where': 'SegmentID IN (' + ','.join("'%07d'" % i for i in nearby_ids) + ')',
         'outFields': 'SegmentID,Street,NodeIDFrom,NodeIDTo,TrafDir,XFrom,YFrom,XTo,YTo',
         'returnGeometry': 'true', 'outSR': 2263, 'resultRecordCount': 2000}
    geo = get_json(LION + '/query', p)
    if geo.get('exceededTransferLimit'):
        raise RuntimeError('Respuesta LION de candidatos truncada.')
    guardar(out / 'lion_cercanos.json', geo)
    guardar(out / 'lion_cercanos.consulta.json', p)
    nodes = ['0021344', '0021396', '0021256', '0021257', '0021389', '0021390']
    node_list = ','.join(repr(node) for node in nodes)
    p = {'f': 'json', 'where': f'NodeIDFrom IN ({node_list}) OR NodeIDTo IN ({node_list})',
         'outFields': 'SegmentID,Street,NodeIDFrom,NodeIDTo', 'returnGeometry': 'false',
         'resultRecordCount': 1000}
    geo = get_json(LION + '/query', p)
    if geo.get('exceededTransferLimit'):
        raise RuntimeError('Respuesta LION de nodos truncada.')
    guardar(out / 'lion_nodos_alternativas.json', geo)
    guardar(out / 'lion_nodos_alternativas.consulta.json', p)
    where = f"segmentid IN ({','.join(map(str, ids))})"

    query('resumen_ids', f'SELECT segmentid, boro, street, fromst, tost, direction, count(*) AS n, min(yr) AS primer_ano, max(yr) AS ultimo_ano WHERE {where} GROUP BY segmentid, boro, street, fromst, tost, direction ORDER BY segmentid')
    query('conteos', f'SELECT * WHERE {where} ORDER BY segmentid, requestid, yr, m, d, hh, mm, direction, :id', paginar=True)
    for attachment in schema.get('metadata', {}).get('attachments', []):
        url = f"{BASE}/api/views/7ym2-wayt/files/{attachment['assetId']}?download=true"
        response = session.get(url, timeout=180)
        if not response.ok:
            raise RuntimeError(f'No se pudo consultar el adjunto {attachment["filename"]}.')
        (out / attachment['filename']).write_bytes(response.content)
    guardar(out / 'consultas.json', log)
    guardar(out / 'manifest.json', {
        'fecha_consulta': datetime.now(ZoneInfo('America/Guatemala')).isoformat(),
        'endpoint': ENDPOINT, 'rowsUpdatedAt': schema.get('rowsUpdatedAt'),
        'radio_m': RADIO_M, 'centro_2263': CENTRO,
        'nota': 'Inventarios agregados; descarga de registros solo de IDs candidatos. Sin credenciales.',
    })
    return out


def leer_hojas_xlsx(path):
    """Lee valores del adjunto oficial sin ejecutar fórmulas ni macros."""
    import zipfile
    import xml.etree.ElementTree as ET
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    sheets = {}
    with zipfile.ZipFile(path) as archive:
        shared = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            shared = [''.join(t.text or '' for t in item.findall('.//m:t', ns))
                      for item in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('m:si', ns)]
        for name in archive.namelist():
            if not re.fullmatch(r'xl/worksheets/sheet\d+\.xml', name):
                continue
            rows = []
            for row in ET.fromstring(archive.read(name)).findall('.//m:row', ns):
                values = []
                for cell in row.findall('m:c', ns):
                    value = cell.find('m:v', ns)
                    value = value.text if value is not None else ''.join(t.text or '' for t in cell.findall('.//m:t', ns))
                    if cell.get('t') == 's':
                        value = shared[int(value)]
                    values.append(value)
                rows.append(values)
            sheets[Path(name).stem] = rows
    return sheets
