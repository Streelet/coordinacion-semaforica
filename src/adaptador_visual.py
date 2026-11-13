"""Adaptador motor SimPy → contrato JSON v1 de la maqueta 3D.

El motor es mesoscópico: sabe CUÁNDO cada vehículo llega a una fila, cruza
W30, llega a W29 y sale, y en qué PUESTO de la fila se formó. No calcula
posiciones en metros. Este adaptador las RECONSTRUYE para dibujarlas:

- Antes de la fila: viaja a velocidad libre hasta su lugar en la cola
  (puesto × 7 m / carriles detrás de la línea de alto).
- En la fila: avanza linealmente hasta la línea de alto, y cruza cuando el motor
  dice que la descarga ocurrió.
- En el tramo: igual, contra la fila de W29.

Las posiciones son una reconstrucción visual; los tiempos, colas, luces y
métricas son los del motor. Uso (desde la raíz del proyecto):

    python src/adaptador_visual.py --salida visualizacion/public/datos/simpy
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from motor_simpy import Parametros, simular, llegadas_poisson
from experimento import FECHA, DESDE, HASTA, T_OBSTR, HORIZONTE, SEMILLA
from exportacion_visual import exportar_corrida, exportar_manifiesto
from demo_animacion import RUTAS as RUTAS_DEMO, puntos_ruta, CAJA

NOMBRES = {'A': 'Tiempos fijos independientes', 'B': 'Tiempos fijos coordinados',
           'C': 'Coordinación + regulación por ocupación'}
# ruta del motor → ruta geométrica, posición de la 1.ª línea de alto, de la 2.ª (si cruza el tramo)
RUTA = {('N', True): ('R1', 92.0, 172.0), ('N', False): ('R2', 92.0, None),
        ('W30O', True): ('R4', 132.0, 212.0), ('W30O', False): ('R3', 132.0, None),
        ('W29E', False): ('R5', 132.0, None)}
CARRILES = {'N': 'carriles_av', 'W30O': 'carriles_tr', 'W29E': 'carriles_tr'}


def _largo(ruta):
    pts = np.array(puntos_ruta(RUTAS_DEMO[ruta]), float)
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())


def trayectoria(v, p: Parametros) -> tuple[str, list]:
    ruta, alto1, alto2 = RUTA[(v.acceso, bool(v.al_tramo))]
    vel = p.v_libre_kmh / 3.6
    lugar1 = max(alto1 - v.puesto_cola1 * p.espacio_veh / getattr(p, CARRILES[v.acceso]), 0.0)
    t_cruce1 = v.t_sale_w30 if v.acceso != 'W29E' else v.t_salida
    k = [(v.t - lugar1 / vel, 0.0), (v.t, lugar1), (t_cruce1, alto1)]
    if alto2 is not None:
        lugar2 = max(alto2 - v.puesto_cola2 * p.espacio_veh / p.carriles_av, alto1)
        llegada = max(v.t_llega_w29, t_cruce1 + (lugar2 - alto1) / vel)
        k += [(llegada, lugar2), (max(v.t_salida, llegada), alto2)]
    fin = _largo(ruta)
    k.append((k[-1][0] + (fin - k[-1][1]) / vel, fin))
    return ruta, k


def recortar(k, t0, t1):
    """Pasa a tiempo relativo [0, t1 − t0], interpolando en los bordes."""
    t = np.array([a for a, _ in k]) - t0
    s = np.array([b for _, b in k])
    t = np.maximum.accumulate(t)
    dur = t1 - t0
    if t[-1] < 0 or t[0] > dur:
        return None
    dentro = (t > 0) & (t < dur)
    tt = np.concatenate([[max(t[0], 0)], t[dentro], [min(t[-1], dur)]])
    tt = np.unique(tt)
    ss = np.interp(tt, t, s)
    pts = [[round(float(a), 2), round(float(b), 2)] for a, b in zip(tt, ss)]
    # quitar tiempos repetidos por redondeo
    limpio = [pts[0]]
    for a in pts[1:]:
        if a[0] > limpio[-1][0]:
            limpio.append(a)
    return limpio


def registro(res, t0: float, t1: float, replica: int) -> dict:
    p, v, s = res.p, res.veh, res.serie
    rng = np.random.default_rng(replica)
    vehiculos = []
    for i, fila in enumerate(v.itertuples(), 1):
        if np.isnan(fila.t_salida):
            continue
        ruta, k = trayectoria(fila, p)
        k = recortar(k, t0, t1)
        if k:
            tipo = 'auto' if not fila.pesado else ('camion' if rng.random() < 0.7 else 'bus')
            vehiculos.append({'id': i, 'tipo': tipo, 'ruta': ruta, 'color': int(rng.integers(6)), 'k': k})
    w = s[(s.t >= t0) & (s.t <= t1)].copy()
    w['t'] -= t0
    tramo = v[v.al_tramo & v.t_salida.notna()]
    bloqueo = (w['bloqueo_w30'].astype(float) * p.muestreo).cumsum()
    m = {'t': w['t'].round(2).tolist(), 'ocupacion_tramo': w['n_tramo'].tolist(),
         'verde_perdido': bloqueo.round(1).tolist(),
         'salidas_tramo': [int(((tramo.t_salida >= t0) & (tramo.t_salida <= t0 + x)).sum()) for x in w['t']],
         'cola_norte': w['cola_N'].tolist(),
         'fuera_de_escena': (np.maximum(w['cola_N'] - 92 * p.carriles_av / p.espacio_veh, 0).astype(int)
                             + np.maximum(w['cola_W30O'] - 132 / p.espacio_veh, 0).astype(int)).tolist()}
    m['t'][0] = 0.0
    primero = w.loc[w['bloqueo_w30'], 't']
    luces = {}
    for nodo, cambios in res.luces.items():
        previo = [c for c in cambios if c[0] <= t0][-1]
        luces[nodo] = [[0.0, previo[1], previo[2]]] + [[round(c[0] - t0, 2), c[1], c[2]] for c in cambios if t0 < c[0] <= t1]
    reg, estado = [], False
    for t, txt in res.bitacora:
        if 'regulación' in txt:
            estado = 'ON' in txt
            if t0 <= t <= t1:
                reg.append([round(t - t0, 2), int(estado)])
    o_ini = max(p.obstr_inicio - t0, 0)
    return {
        'meta': {'estrategia': p.estrategia, 'nombre': NOMBRES[p.estrategia], 'duracion': t1 - t0, 'es_demo': False,
                 'aviso': 'Motor SimPy con demanda FICTICIA y parámetros supuestos; posiciones reconstruidas.',
                 'parametros': {'velocidad_libre': p.v_libre_kmh / 3.6, 'ciclo': p.ciclo, 'desfase_w29': p.desfase_w29,
                                'K': p.K, 'umbrales_regulacion': [p.frac_L * p.K, p.frac_H * p.K] if p.estrategia == 'C' else None,
                                'obstruccion_min': p.obstr_dur / 60, 'ventana': f'{FECHA} desde t={t0:.0f} s de las {DESDE}'}},
        'red': {'rutas': {r: puntos_ruta(e) for r, e in RUTAS_DEMO.items()}, 'radio_giro': 6.0,
                'calles': [{'nombre': 'Seventh Ave', 'de': [0, 140], 'a': [0, -140], 'ancho': 9},
                           {'nombre': 'W 30th St', 'de': [-140, 40], 'a': [140, 40], 'ancho': 8},
                           {'nombre': 'W 29th St', 'de': [140, -40], 'a': [-140, -40], 'ancho': 8}],
                'nodos': {'W30': [0, 40], 'W29': [0, -40]},
                'lineas_alto': [{'nodo': 'W30', 'fase': 'av', 'x': 0, 'y': 40 + CAJA, 'a_lo_largo': 'x'},
                                {'nodo': 'W30', 'fase': 'tr', 'x': -CAJA, 'y': 40, 'a_lo_largo': 'y'},
                                {'nodo': 'W29', 'fase': 'av', 'x': 0, 'y': -40 + CAJA, 'a_lo_largo': 'x'},
                                {'nodo': 'W29', 'fase': 'tr', 'x': CAJA, 'y': -40, 'a_lo_largo': 'y'}],
                'tramo': {'de': [0, 40 - CAJA], 'a': [0, -40 + CAJA], 'capacidad': p.K}},
        'obstruccion': {'t_inicio': o_ini, 't_fin': min(p.obstr_inicio + p.obstr_dur - t0, t1 - t0),
                        'x': 0, 'y': -30.0, 'lado': -3.4,
                        'intervalo_paso_s': 3600 / (p.sat_carril * max(p.carriles_av - p.carriles_bloqueados, 1))},
        'semaforos': luces, 'regulacion': reg, 'vehiculos': vehiculos, 'metricas': m,
        'resumen': {'t_cola_llega_w30': float(primero.iloc[0]) if len(primero) else None,
                    'verde_perdido': float(bloqueo.iloc[-1]), 'salidas_tramo': m['salidas_tramo'][-1],
                    'ocupacion_maxima': int(w['n_tramo'].max())},
    }


def exportar(iv, salida: Path, duracion_min=10, replica=1, antes=300, despues=900):
    ll = llegadas_poisson(iv, FECHA, DESDE, HASTA, semilla=SEMILLA + replica)
    t0, t1 = T_OBSTR - antes, T_OBSTR + duracion_min * 60 + despues
    escenarios = []
    for e in 'ABC':
        p = Parametros(estrategia=e, obstr_inicio=T_OBSTR, obstr_dur=duracion_min * 60)
        res = simular(p, ll, HORIZONTE, registrar_luces=True)
        archivo = salida / f'simpy_{e}.json'
        exportar_corrida(registro(res, t0, t1, replica), archivo, motor='simpy',
                         entradas_id=f'base-20261112-{FECHA}-r{replica}', replica_id=replica)
        escenarios.append({'id': e, 'archivo': archivo.name})
        print(e, archivo, f'{archivo.stat().st_size // 1024} KB')
    exportar_manifiesto(escenarios, salida / 'manifest.json')


if __name__ == '__main__':
    raiz = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser()
    ap.add_argument('--salida', type=Path, default=raiz / 'resultados' / 'simpy')
    ap.add_argument('--duracion', type=float, default=10)
    ap.add_argument('--replica', type=int, default=1)
    a = ap.parse_args()
    exportar(pd.read_csv(raiz / 'datos/procesados/intervalos.csv'), a.salida, a.duracion, a.replica)
