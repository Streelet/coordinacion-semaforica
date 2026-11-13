"""Motor SimPy del corredor Séptima Avenida (W30 → tramo → W29).

Modelo mesoscópico de colas (no microscópico): cada acceso es una fila FIFO
que descarga un vehículo cada `headway` segundos mientras su semáforo está en
verde y hay espacio aguas abajo. El tramo interno W30→W29 es un almacén finito
de K vehículos (avenida = almacén agregado de carriles). Una obstrucción
reduce los carriles que descargan en W29; no borra vehículos.

Estrategias (comparación en escalera A → B → C):
    A  tiempos fijos independientes (desfase de W29 sin relación con el viaje)
    B  mismos tiempos, desfase de W29 = tiempo de viaje libre del tramo
    C  B + regulación por ocupación del tramo con histéresis (H, L): al activarse,
       W30 retiene la entrada al tramo y corta el verde de la avenida (tras un
       verde mínimo) para darlo, después de un despeje, a la calle W30.

Todos los valores de `Parametros` son SUPUESTOS DECLARADOS (ver notebook 02),
salvo la demanda, que viene de la base ficticia (datos/procesados).
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field, asdict, replace

import numpy as np
import pandas as pd
import simpy

# ------------------------------------------------------------------ parámetros
@dataclass(frozen=True)
class Parametros:
    estrategia: str = 'A'
    # Plan semafórico (s). Avenida: verde [0, 28), amarillo, todo rojo;
    # transversal: verde [33, 55), amarillo, todo rojo. Ciclo 60 s.
    ciclo: float = 60.0
    verde_av: float = 28.0
    verde_tr: float = 22.0
    amarillo: float = 3.0
    todo_rojo: float = 2.0
    desfase_w30: float = 0.0
    desfase_w29_indep: float = 40.0      # A: elegido sin mirar el tiempo de viaje
    # Capacidad
    carriles_av: int = 3
    carriles_tr: int = 1
    sat_carril: float = 1800.0           # veh/h de verde por carril
    pce_pesado: float = 1.5              # camión/bus ocupa 1.5 "autos" de tiempo
    # Geometría del tramo
    largo_tramo: float = 80.0            # m
    espacio_veh: float = 7.0             # m por vehículo detenido
    v_libre_kmh: float = 25.0
    almacen_cuadra_previa: int = 33      # Séptima W31→W30, en vehículos
    # Estrategia C
    frac_H: float = 0.8
    frac_L: float = 0.6
    verde_min: float = 10.0
    despeje: float = 5.0
    # Obstrucción (segundos desde el inicio de la corrida)
    obstr_inicio: float | None = None
    obstr_dur: float = 0.0
    carriles_bloqueados: int = 2
    # Simulación
    dt: float = 0.5                      # paso de sondeo cuando una fila está detenida
    muestreo: float = 5.0                # serie temporal

    @property
    def K(self) -> int:
        return int(self.largo_tramo // self.espacio_veh) * self.carriles_av

    @property
    def tau(self) -> float:
        """Tiempo de viaje libre del tramo: 3.6·L/v (s)."""
        return 3.6 * self.largo_tramo / self.v_libre_kmh

    @property
    def desfase_w29(self) -> float:
        if self.estrategia == 'A':
            return self.desfase_w29_indep
        return round((self.desfase_w30 + self.tau) % self.ciclo)


# ------------------------------------------------------------------- demanda
RUTA = {(33804, 'entra_tramo'): ('N', True), (33804, 'otro'): ('N', False),
        (33803, 'entra_tramo'): ('W30O', True), (33803, 'otro'): ('W30O', False),
        (33894, 'otro'): ('W29E', False), (33894, 'entra_tramo'): ('W29E', False)}


def llegadas_base(iv: pd.DataFrame, vh: pd.DataFrame, fecha: str, desde: str, hasta: str) -> pd.DataFrame:
    """Réplica 0: los vehículos exactos de la tabla `vehiculos` en la ventana [desde, hasta)."""
    sel = iv[(iv.fecha == fecha) & (iv.hora_inicio >= desde) & (iv.hora_inicio < hasta)]
    t0 = _segundos(desde)
    v = vh.merge(sel[['intervalo_id', 'acceso_id', 'hora_inicio']], on='intervalo_id')
    v['t'] = v['hora_inicio'].map(_segundos) - t0 + v['segundo_llegada']
    return _formatear(v)


def llegadas_poisson(iv: pd.DataFrame, fecha: str, desde: str, hasta: str, semilla: int) -> pd.DataFrame:
    """Réplicas 1..R: se re-sortean con las MISMAS reglas (λ, proporciones) y otra semilla."""
    rng = np.random.default_rng(semilla)
    sel = iv[(iv.fecha == fecha) & (iv.hora_inicio >= desde) & (iv.hora_inicio < hasta)]
    t0 = _segundos(desde)
    filas = []
    for r in sel.itertuples():
        n = rng.poisson(r.tasa_llegada_vph * 0.25)
        u = rng.random(n)
        tipo = np.where(u < r.prop_pesados * 0.7, 'camion', np.where(u < r.prop_pesados, 'bus', 'auto'))
        mov = np.where(rng.random(n) < r.prop_hacia_tramo, 'entra_tramo', 'otro')
        t = _segundos(r.hora_inicio) - t0 + rng.uniform(0, 900, n)
        filas.append(pd.DataFrame({'t': t, 'acceso_id': r.acceso_id, 'tipo_vehiculo': tipo, 'movimiento': mov}))
    return _formatear(pd.concat(filas))


def llegadas_constantes(acceso: str, vph: float, duracion: float, semilla: int, al_tramo: bool = False) -> pd.DataFrame:
    """Poisson de tasa fija en un solo acceso (para verificaciones, p. ej. Webster)."""
    rng = np.random.default_rng(semilla)
    n = rng.poisson(vph * duracion / 3600)
    return pd.DataFrame({'t': np.sort(rng.uniform(0, duracion, n)), 'acceso': acceso,
                         'al_tramo': al_tramo, 'pesado': False}).reset_index(drop=True)


def _segundos(hhmm: str) -> int:
    h, m = hhmm.split(':')
    return int(h) * 3600 + int(m) * 60


def _formatear(v: pd.DataFrame) -> pd.DataFrame:
    ruta = [RUTA[(a, m)] for a, m in zip(v['acceso_id'], v['movimiento'])]
    out = pd.DataFrame({'t': v['t'].to_numpy(), 'acceso': [r[0] for r in ruta],
                        'al_tramo': [r[1] for r in ruta], 'pesado': (v['tipo_vehiculo'] != 'auto').to_numpy()})
    return out.sort_values('t', kind='stable').reset_index(drop=True)


# -------------------------------------------------------------------- motor
SENAL = {'N': ('W30', 'av'), 'W30O': ('W30', 'tr'), 'T': ('W29', 'av'), 'W29E': ('W29', 'tr')}


class Corredor:
    def __init__(self, p: Parametros, llegadas: pd.DataFrame, horizonte: float, registrar_luces: bool = False):
        self.p, self.horizonte = p, horizonte
        self.env = simpy.Environment()
        self.filas = {a: deque() for a in SENAL}
        self.n_tramo = 0
        self.regulando = False
        self._corte = (None, 0.0)        # (ciclo, instante) en que C cortó la avenida en W30
        self.veh = llegadas.copy()
        for c in ('t_sale_w30', 't_llega_w29', 't_salida', 'puesto_cola1', 'puesto_cola2'):
            self.veh[c] = np.nan
        self.registro_luces: dict[str, list] = {'W30': [], 'W29': []}
        self.bitacora: list[tuple[float, str]] = []
        self.serie: list[dict] = []
        self.generados = 0
        self.env.process(self._llegadas())
        for a in SENAL:
            self.env.process(self._descarga(a))
        self.env.process(self._observador())
        if registrar_luces:
            self.env.process(self._registrar_luces())

    # ---- señales
    def _fase(self, t: float, nodo: str) -> tuple[str, float, int]:
        p = self.p
        des = p.desfase_w30 if nodo == 'W30' else p.desfase_w29
        x = (t - des) % p.ciclo
        k = math.floor((t - des) / p.ciclo)
        ini_tr = p.verde_av + p.amarillo + p.todo_rojo
        if x < p.verde_av:
            return 'av', x, k
        if ini_tr <= x < ini_tr + p.verde_tr:
            return 'tr', x, k
        return '-', x, k

    def verde(self, t: float, nodo: str) -> str:
        fase, x, k = self._fase(t, nodo)
        if nodo == 'W30' and self.p.estrategia == 'C' and fase == 'av':
            if self._corte[0] != k and self.regulando and x >= self.p.verde_min:
                self._corte = (k, x)
                self.bitacora.append((t, 'C: corta verde de avenida en W30'))
            if self._corte[0] == k:
                return '-' if x < self._corte[1] + self.p.despeje else 'tr'
        return fase

    def luces(self, t: float, nodo: str) -> tuple[str, str]:
        """Colores (avenida, transversal) para la bitácora visual: 'V', 'A' o 'R'."""
        v = self.verde(t, nodo)
        if v == 'av':
            return 'V', 'R'
        if v == 'tr':
            return 'R', 'V'
        p, (_, x, k) = self.p, self._fase(t, nodo)
        if nodo == 'W30' and self._corte[0] == k and x < p.verde_av:
            return ('A' if x < self._corte[1] + p.amarillo else 'R'), 'R'
        if p.verde_av <= x < p.verde_av + p.amarillo:
            return 'A', 'R'
        ini = p.verde_av + p.amarillo + p.todo_rojo + p.verde_tr
        return 'R', ('A' if ini <= x < ini + p.amarillo else 'R')

    def _registrar_luces(self):
        while True:
            t = self.env.now
            for nodo, cambios in self.registro_luces.items():
                e = self.luces(t, nodo)
                if not cambios or cambios[-1][1:] != list(e):
                    cambios.append([t, *e])
            yield self.env.timeout(self.p.dt)

    def obstruido(self, t: float) -> bool:
        p = self.p
        return p.obstr_inicio is not None and p.obstr_inicio <= t < p.obstr_inicio + p.obstr_dur

    # ---- reglas de paso
    def _headway(self, acceso: str, pesado: bool, t: float) -> float:
        p = self.p
        carriles = p.carriles_tr if SENAL[acceso][1] == 'tr' else p.carriles_av
        if acceso == 'T' and self.obstruido(t):
            carriles = max(p.carriles_av - p.carriles_bloqueados, 0)
        if carriles == 0:
            return math.inf
        return 3600 / (p.sat_carril * carriles) * (p.pce_pesado if pesado else 1.0)

    def _puede_entrar_tramo(self) -> bool:
        if self.p.estrategia == 'C' and self.regulando:
            return False
        return self.n_tramo < self.p.K

    # ---- procesos
    def _llegadas(self):
        for i, (t, acceso) in enumerate(zip(self.veh['t'], self.veh['acceso'])):
            yield self.env.timeout(max(t - self.env.now, 0))
            self.veh.at[i, 'puesto_cola1'] = len(self.filas[acceso])
            self.filas[acceso].append(i)
            self.generados += 1

    def _descarga(self, acceso: str):
        env, fila, (nodo, mov) = self.env, self.filas[acceso], SENAL[acceso]
        while True:
            t = env.now
            if not fila or self.verde(t, nodo) != mov:
                yield env.timeout(self.p.dt)
                continue
            i = fila[0]
            al_tramo = acceso in ('N', 'W30O') and self.veh.at[i, 'al_tramo']
            if al_tramo and not self._puede_entrar_tramo():
                yield env.timeout(self.p.dt)
                continue
            h = self._headway(acceso, self.veh.at[i, 'pesado'], t)
            if math.isinf(h):
                yield env.timeout(self.p.dt)
                continue
            fila.popleft()
            if acceso in ('N', 'W30O'):
                self.veh.at[i, 't_sale_w30'] = t
            if al_tramo:
                self.n_tramo += 1
                self._actualizar_regulacion(t)
                env.process(self._recorrer_tramo(i))
            else:
                if acceso == 'T':
                    self.n_tramo -= 1
                    self._actualizar_regulacion(t)
                self.veh.at[i, 't_salida'] = t
            yield env.timeout(h)

    def _recorrer_tramo(self, i: int):
        yield self.env.timeout(self.p.tau)
        self.veh.at[i, 't_llega_w29'] = self.env.now
        self.veh.at[i, 'puesto_cola2'] = len(self.filas['T'])
        self.filas['T'].append(i)

    def _actualizar_regulacion(self, t: float):
        if self.p.estrategia != 'C':
            return
        K = self.p.K
        if not self.regulando and self.n_tramo >= self.p.frac_H * K:
            self.regulando = True
            self.bitacora.append((t, f'C: regulación ON (ocupación {self.n_tramo}/{K})'))
        elif self.regulando and self.n_tramo <= self.p.frac_L * K:
            self.regulando = False
            self.bitacora.append((t, f'C: regulación OFF (ocupación {self.n_tramo}/{K})'))

    def _observador(self):
        p, ob_prev = self.p, False
        while True:
            t = self.env.now
            ob = self.obstruido(t)
            if ob != ob_prev:
                self.bitacora.append((t, 'obstrucción INICIA' if ob else 'obstrucción TERMINA'))
                ob_prev = ob
            cabeza_bloq = bool(self.filas['N']) and self.verde(t, 'W30') == 'av' and \
                self.veh.at[self.filas['N'][0], 'al_tramo'] and self.n_tramo >= p.K
            salidos = int(self.veh['t_salida'].notna().sum())
            en_filas = sum(len(f) for f in self.filas.values())
            en_movimiento = self.n_tramo - len(self.filas['T'])
            self.serie.append({'t': t, 'n_tramo': self.n_tramo, 'cola_N': len(self.filas['N']),
                               'cola_W30O': len(self.filas['W30O']), 'cola_T': len(self.filas['T']),
                               'cola_W29E': len(self.filas['W29E']), 'obstruccion': ob,
                               'regulando': self.regulando, 'bloqueo_w30': cabeza_bloq,
                               'senal_w30': self.verde(t, 'W30'), 'senal_w29': self.verde(t, 'W29'),
                               'generados': self.generados, 'salidos': salidos,
                               'en_sistema': en_filas + en_movimiento})
            yield self.env.timeout(p.muestreo)

    def correr(self) -> 'Resultado':
        self.env.run(until=self.horizonte)
        return Resultado(self.p, self.veh, pd.DataFrame(self.serie), self.bitacora, self.horizonte, self.registro_luces)


# --------------------------------------------------------------- resultados
@dataclass
class Resultado:
    p: Parametros
    veh: pd.DataFrame
    serie: pd.DataFrame
    bitacora: list
    horizonte: float
    luces: dict = field(default_factory=dict)

    def tiempos(self) -> pd.DataFrame:
        v = self.veh.copy()
        libre = np.where(v['al_tramo'], self.p.tau, 0.0)
        v['espera'] = v['t_salida'] - v['t'] - libre
        return v

    def metricas(self, desde: float = 0.0) -> dict:
        """Indicadores para vehículos que llegan después de `desde` (calentamiento)."""
        v = self.tiempos()
        v = v[v['t'] >= desde]
        s = self.serie[self.serie['t'] >= desde]
        dt = self.p.muestreo
        hechos = v.dropna(subset=['t_salida'])
        m = {'estrategia': self.p.estrategia,
             'vehiculos': len(v), 'completados': len(hechos), 'pendientes_al_cierre': int(v['t_salida'].isna().sum()),
             'espera_media_s': hechos['espera'].mean(),
             'espera_p95_s': hechos['espera'].quantile(0.95),
             'ocupacion_max_tramo': int(s['n_tramo'].max()),
             'cola_max_septima': int(s['cola_N'].max()),
             'cola_max_w30': int(s['cola_W30O'].max()),
             's_cola_llega_w31': float((s['cola_N'] > self.p.almacen_cuadra_previa).sum() * dt),
             's_bloqueo_w30': float(s['bloqueo_w30'].sum() * dt)}
        for a, g in hechos.groupby('acceso'):
            m[f'espera_{a}_s'] = g['espera'].mean()
        return m


def simular(p: Parametros, llegadas: pd.DataFrame, horizonte: float, registrar_luces: bool = False) -> Resultado:
    return Corredor(p, llegadas, horizonte, registrar_luces).correr()


# ----------------------------------------------------------- verificaciones
def verificar_conservacion(r: Resultado) -> bool:
    """generados = salidos + en el sistema, en cada instante muestreado; 0 ≤ n ≤ K."""
    s = r.serie
    ok_balance = (s['generados'] == s['salidos'] + s['en_sistema']).all()
    ok_cotas = s['n_tramo'].between(0, r.p.K).all()
    return bool(ok_balance and ok_cotas)


def verificar_little(r: Resultado) -> dict:
    """Ley de Little en el tramo: L (ocupación media) = λ (entradas/s) × W (tiempo medio dentro)."""
    v = r.veh.dropna(subset=['t_sale_w30', 't_salida'])
    v = v[v['al_tramo']]
    T = r.horizonte
    W = (v['t_salida'] - v['t_sale_w30']).mean()
    lam = len(v) / T
    L_obs = r.serie['n_tramo'].mean()
    return {'L_observada': L_obs, 'lambda_x_W': lam * W, 'error_rel': abs(L_obs - lam * W) / L_obs}


def webster(q_vph: float, p: Parametros, mov: str = 'tr') -> float:
    """Demora media de Webster (1958) para un acceso aislado con llegadas aleatorias."""
    g = p.verde_tr if mov == 'tr' else p.verde_av
    carriles = p.carriles_tr if mov == 'tr' else p.carriles_av
    c, s, q = p.ciclo, p.sat_carril * carriles / 3600, q_vph / 3600
    lam = g / c
    x = q / (s * lam)
    d = c * (1 - lam) ** 2 / (2 * (1 - lam * x)) + x ** 2 / (2 * q * (1 - x))
    return d - 0.65 * (c / q ** 2) ** (1 / 3) * x ** (2 + 5 * lam)


def grado_saturacion(q_vph: float, p: Parametros, mov: str, carriles: int | None = None) -> float:
    """ρ = demanda / capacidad, con capacidad = s · carriles · g / C."""
    g = p.verde_tr if mov == 'tr' else p.verde_av
    n = carriles if carriles is not None else (p.carriles_tr if mov == 'tr' else p.carriles_av)
    return q_vph / (p.sat_carril * n * g / p.ciclo)
