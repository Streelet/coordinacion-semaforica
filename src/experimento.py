"""Experimento del paso 13: estrategias A/B/C × duración de la obstrucción × réplicas.

Diseño:
- Ventana: miércoles 2026-03-04, 16:30–18:30 (sin lluvia ni evento); los
  primeros 15 min son calentamiento; obstrucción a las 17:00 (t = 1800 s).
- Réplica r: llegadas re-sorteadas con las reglas de la base (semilla 20261113 + r).
  Números aleatorios comunes: A, B y C de la misma réplica reciben las MISMAS llegadas.
- Horizonte: 2 h de llegadas + 30 min de vaciado, para que no quede nadie
  (si quedara alguien, se reporta en `pendientes_al_cierre`).
"""
from __future__ import annotations

from dataclasses import replace
from itertools import product

import numpy as np
import pandas as pd
from scipy import stats

from motor_simpy import Parametros, simular, llegadas_poisson

FECHA, DESDE, HASTA = '2026-03-04', '16:30', '18:30'
T_OBSTR, CALENT, HORIZONTE = 1800.0, 900.0, 7200.0 + 1800.0
SEMILLA = 20261113
METRICAS = ['espera_media_s', 'espera_N_s', 'espera_W30O_s', 'cola_max_septima',
            's_cola_llega_w31', 's_bloqueo_w30', 'ocupacion_max_tramo', 'pendientes_al_cierre']


def correr(iv: pd.DataFrame, duraciones, replicas: int, base: Parametros = Parametros(),
           estrategias='ABC', etiqueta: str = '') -> pd.DataFrame:
    filas = []
    for r in range(1, replicas + 1):
        ll = llegadas_poisson(iv, FECHA, DESDE, HASTA, semilla=SEMILLA + r)
        for d, e in product(duraciones, estrategias):
            p = replace(base, estrategia=e, obstr_inicio=T_OBSTR if d > 0 else None, obstr_dur=d * 60)
            res = simular(p, ll, HORIZONTE)
            m = res.metricas(desde=CALENT)
            s = res.serie
            post = s[s.t >= T_OBSTR]
            lleno = post.loc[post.n_tramo >= p.K, 't']
            w31 = post.loc[post.cola_N > p.almacen_cuadra_previa, 't']
            m.update(replica=r, duracion_min=d, etiqueta=etiqueta,
                     min_hasta_tramo_lleno=(lleno.iloc[0] - T_OBSTR) / 60 if len(lleno) else np.nan,
                     min_hasta_w31=(w31.iloc[0] - T_OBSTR) / 60 if len(w31) else np.nan)
            filas.append(m)
    return pd.DataFrame(filas)


def ic_pareado(df: pd.DataFrame, metrica: str, de: str, a: str, por='duracion_min', nivel=0.95) -> pd.DataFrame:
    """Diferencia media emparejada (a − de) por réplica, con IC t de Student."""
    w = df.pivot_table(index=[por, 'replica'], columns='estrategia', values=metrica)
    dif = (w[a] - w[de]).groupby(level=0)
    out = dif.agg(['mean', 'std', 'count'])
    t = stats.t.ppf((1 + nivel) / 2, out['count'] - 1)
    out['ic_inf'] = out['mean'] - t * out['std'] / np.sqrt(out['count'])
    out['ic_sup'] = out['mean'] + t * out['std'] / np.sqrt(out['count'])
    out['comparacion'] = f'{a} − {de}'
    return out.drop(columns='std')
