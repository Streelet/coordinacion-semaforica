"""Adaptador motor SimPy → contrato JSON v1 de la maqueta 3D.

El motor es mesoscópico: sabe CUÁNDO cada vehículo llega a una fila, cruza
W30, llega a W29 y sale, y en qué PUESTO de la fila se formó. No calcula
posiciones en metros. Este adaptador las RECONSTRUYE para dibujarlas:

- Antes de la fila: viaja a velocidad libre hasta su lugar en la cola
  (puesto × 7 m / carriles detrás de la línea de alto). La Séptima se dibuja con
  3 carriles; cada vehículo recibe uno por turno.
- Separación: nadie se acerca al de adelante a menos de su largo + 2.5 m.
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
from demo_animacion import CAJA, LARGO

NOMBRES = {'A': 'Tiempos fijos independientes', 'B': 'Tiempos fijos coordinados',
           'C': 'Coordinación + regulación por ocupación'}
CARRILES_X = [-3.0, 0.0, 3.0]   # la Séptima (9 m) se dibuja con 3 carriles, como en el motor
Y_DESVIO = (-8.0, -20.0)        # tramo donde se cambian al carril libre (y), antes del camión
CAMION = {'x': 0.0, 'lado': -2.0, 'y': -26.0, 'angulo': 45.0}   # atravesado sobre 2 carriles


def geometria(acceso: str, al_tramo: bool, carril: int, desvia: bool = False):
    """(nombre, puntos, línea de alto 1, inicio del tramo, línea de alto 2) en metros sobre la ruta.

    "inicio del tramo" es la s donde la coordenada común del tramo vale 0 (y = 48),
    para poder comparar vehículos de la Séptima y de W30 en el mismo carril.
    """
    dx = CARRILES_X[carril]
    if al_tramo and desvia and acceso in ('N', 'W30O'):
        # Camión atravesado en los carriles oeste y central: se cambia al carril este antes de él.
        x3 = CARRILES_X[2]
        extra = float(np.hypot(x3 - dx, Y_DESVIO[0] - Y_DESVIO[1])) - (Y_DESVIO[0] - Y_DESVIO[1])
        cola = [[dx, Y_DESVIO[0]], [x3, Y_DESVIO[1]], [x3, -40], [x3, -140]]
        if acceso == 'N':
            return f'R1c{carril}d', [[dx, 140], [dx, 40]] + cola, 92.0, 92.0, 172.0 + extra
        inicio = 140 + dx - 8
        return 'R4d', [[-140, 40], [dx, 40]] + cola, 132.0, inicio, inicio + 80 + extra
    if acceso == 'N' and al_tramo:
        return f'R1c{carril}', [[dx, 140], [dx, 40], [dx, -40], [dx, -140]], 92.0, 92.0, 172.0
    if acceso == 'N':
        return f'R2c{carril}', [[dx, 140], [dx, 40], [140, 40]], 92.0, None, None
    if acceso == 'W30O' and al_tramo:    # gira a la derecha y entra por el carril oeste
        inicio = 140 + dx - 8                  # s donde y = 48 si se prolonga el tramo
        return 'R4', [[-140, 40], [dx, 40], [dx, -40], [dx, -140]], 132.0, inicio, inicio + 80
    if acceso == 'W30O':
        return 'R3', [[-140, 40], [140, 40]], 132.0, None, None
    return 'R5', [[140, -40], [-140, -40]], 132.0, None, None


def _largo(puntos):
    pts = np.array(puntos, float)
    return float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum())


def trayectoria(v, p: Parametros, carril: int, desvia: bool = False) -> tuple[str, list, list]:
    ruta, puntos, alto1, _, alto2 = geometria(v.acceso, bool(v.al_tramo), carril, desvia)
    vel = p.v_libre_kmh / 3.6
    n1 = p.carriles_av if v.acceso == 'N' else 1
    lugar1 = max(alto1 - v.puesto_cola1 / n1 * p.espacio_veh, 0.0)
    t_cruce1 = v.t_sale_w30 if v.acceso != 'W29E' else v.t_salida
    k = [(v.t - lugar1 / vel, 0.0), (v.t, lugar1), (t_cruce1, alto1)]
    if alto2 is not None:
        lugar2 = max(alto2 - v.puesto_cola2 / p.carriles_av * p.espacio_veh, alto1)
        llegada = max(v.t_llega_w29, t_cruce1 + (lugar2 - alto1) / vel)
        k += [(llegada, lugar2), (max(v.t_salida, llegada), alto2)]
    fin = _largo(puntos)
    k.append((k[-1][0] + (fin - k[-1][1]) / vel, fin))
    return ruta, puntos, k


DT_VIS = 0.5        # s, rejilla para separar vehículos
HOLGURA = 2.5       # m libres entre el final de un vehículo y el siguiente


def separar(v, p: Parametros, t0: float, t1: float, tipos: dict) -> tuple[dict, dict]:
    """Trayectorias visuales sin solapes: nadie se acerca a menos de largo + holgura del de adelante.

    La Séptima se dibuja con 3 carriles (como en el motor). Cada vehículo de la Séptima
    recibe un carril por turno al cruzar W30; quien entra desde W30 usa el carril oeste.
    Se procesan en el orden en que cruzan y cada uno se limita por su líder en el mismo
    carril de su fila y, dentro del tramo, por el líder de su carril. Luego se limita la
    velocidad para que no haya saltos. Las métricas no cambian: son las del motor.
    """
    vel = p.v_libre_kmh / 3.6
    grid = np.arange(t0 - 900, t1 + DT_VIS, DT_VIS)
    v = v[v.t_salida.notna()].copy()
    v['cruce1'] = np.where(v.acceso == 'W29E', v.t_salida, v.t_sale_w30)
    pos, inicio_tramo, ult_fila, ult_tramo, rutas, info = {}, {}, {}, {}, {}, {}
    turno, ult_w30e, inicio_e, ult_nativo2 = 0, None, {}, None
    obst = (p.obstr_inicio, p.obstr_inicio + p.obstr_dur) if p.obstr_inicio is not None and p.carriles_bloqueados >= 2 else None
    for i, f in v.sort_values(['cruce1', 't']).iterrows():
        if f.acceso == 'N':
            carril, turno = turno % 3, turno + 1
        else:
            carril = 0
        desvia = bool(f.al_tramo) and carril != 2 and obst is not None and \
            f.t_sale_w30 < obst[1] and f.t_salida > obst[0]
        ruta, puntos, k = trayectoria(f, p, carril, desvia)
        _, _, alto1, ini, alto2 = geometria(f.acceso, bool(f.al_tramo), carril, desvia)
        extra = (alto2 - ini - 80) if desvia else 0.0
        rutas[ruta] = puntos
        kt, ks = np.maximum.accumulate(np.array([a for a, _ in k])), np.array([b for _, b in k])
        x = np.interp(grid, kt, ks)
        x[grid < kt[0]] = -1e9
        clave = (f.acceso, carril)
        lider = ult_fila.get(clave)
        if lider is not None:                       # misma fila y carril: comparten calle hasta el centro del cruce
            hueco = LARGO[tipos[lider]] + HOLGURA
            m = pos[lider] <= alto1 + CAJA + hueco
            x[m] = np.minimum(x[m], pos[lider][m] - hueco)
        lt = (ult_nativo2 if carril == 2 else ult_tramo.get(carril)) if f.al_tramo else None
        if lt is not None:                          # dentro del tramo: líder de su carril, venga de donde venga
            hueco = LARGO[tipos[lt]] + HOLGURA
            lc = pos[lt] - inicio_tramo[lt]
            m = lc >= 0                              # en el tramo y después, hacia el sur
            if desvia:                               # su carril solo hasta que el líder termina el desvío
                m &= lc < (48 - Y_DESVIO[1]) + hueco
            x[m] = np.minimum(x[m], lc[m] + ini - hueco)
            x[lc < 0] = np.minimum(x[lc < 0], alto1)   # no entra antes que su líder
        l2 = ult_tramo.get(2) if desvia else None
        if l2 is not None:                          # al desviarse: detrás del último que va por el carril libre
            hueco = LARGO[tipos[l2]] + HOLGURA
            lc = pos[l2] - inicio_tramo[l2]
            tope = np.maximum(ini + (48 - Y_DESVIO[0]) - 6, lc + ini + extra - hueco)
            x = np.minimum(x, tope)
        lm = ult_tramo.get(2) if (f.al_tramo and carril == 2 and not desvia) else None
        if lm is not None and lm != lt:             # carril libre: también detrás del último que se cambió a él
            hueco = LARGO[tipos[lm]] + HOLGURA
            lc = pos[lm] - inicio_tramo[lm]
            m = lc >= (48 - Y_DESVIO[0])
            x[m] = np.minimum(x[m], lc[m] + ini - hueco)
        sale_w30e = ruta.startswith(('R2', 'R3'))
        off_e = (100 - CARRILES_X[carril]) if ruta.startswith('R2') else 140.0   # s donde x = 0 sobre W30 este
        le = ult_w30e if sale_w30e else None
        if le is not None:                          # salida por W30 hacia el este: un solo carril compartido
            hueco = LARGO[tipos[le]] + HOLGURA
            lx = pos[le] - inicio_e[le]
            m = lx >= 0
            x[m] = np.minimum(x[m], lx[m] + off_e - hueco)
        vmax = 1.5 * vel * DT_VIS
        for j in range(1, len(x)):
            if x[j - 1] > -1e8 and x[j] > x[j - 1] + vmax:
                x[j] = x[j - 1] + vmax
        x = np.maximum.accumulate(x)
        info[i] = (ruta, _largo(puntos))
        x[x >= info[i][1]] = 1e9                    # al terminar su ruta sale de escena: ya no limita a nadie
        pos[i] = x
        ult_fila[clave] = i
        if sale_w30e:
            inicio_e[i] = off_e
            ult_w30e = i
        if f.al_tramo:
            inicio_tramo[i] = ini + extra
            ult_tramo[carril] = i
            if carril == 2:
                ult_nativo2 = i
            if desvia:
                ult_tramo[2] = i
    out = {}
    fin_vis = grid >= t0
    for i, x in pos.items():
        ruta, fin = info[i]
        vis = fin_vis & (x >= 0) & (x < fin)
        x = np.where(x > 1e8, fin, x)
        if not vis.any():
            continue
        idx = np.flatnonzero(vis)
        a, b = idx[0], min(idx[-1] + 1, len(x) - 1)
        tt, xx = grid[a:b + 1] - t0, np.minimum(x[a:b + 1], fin)
        d = np.diff(xx)                              # conservar solo los cambios de velocidad
        quiebre = np.r_[True, np.abs(np.diff(d)) > 1e-3, True] if len(xx) > 1 else np.array([True])
        out[i] = (ruta, [[round(float(t), 2), round(float(s), 2)] for t, s in zip(tt[quiebre], xx[quiebre])])
    return out, rutas


def registro(res, t0: float, t1: float, replica: int) -> dict:
    p, v, s = res.p, res.veh, res.serie
    rng = np.random.default_rng(replica)
    tipos = {i: ('auto' if not pe else ('camion' if rng.random() < 0.7 else 'bus')) for i, pe in v['pesado'].items()}
    trayectos, rutas = separar(v, p, t0, t1, tipos)
    vehiculos = [{'id': int(i) + 1, 'tipo': tipos[i], 'ruta': ruta, 'color': int(i % 6), 'k': k}
                 for i, (ruta, k) in sorted(trayectos.items())]
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
                                'obstruccion_min': p.obstr_dur / 60,
                                'capacidad_normal_vph': round(p.sat_carril * p.carriles_av * p.verde_av / p.ciclo),
                                'capacidad_reducida_vph': round(p.sat_carril * max(p.carriles_av - p.carriles_bloqueados, 1) * p.verde_av / p.ciclo),
                                'almacen_cuadra_previa': p.almacen_cuadra_previa,
                                'carriles_av': p.carriles_av, 'carriles_bloqueados': p.carriles_bloqueados, 'ventana': f'{FECHA} desde t={t0:.0f} s de las {DESDE}'}},
        'red': {'rutas': dict(sorted(rutas.items())), 'radio_giro': 4.0,
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
                        **CAMION, 'carriles_bloqueados': p.carriles_bloqueados,
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
