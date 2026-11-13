"""Genera datos de DEMOSTRACIÓN para la visualización (carpeta visualizacion/).

IMPORTANTE: esto NO es el modelo del proyecto ni produce resultados. Es un
simulador de juguete (un carril por calle, demanda constante, 12 minutos) que
sirve para dos cosas:

1. Tener movimiento realista con el cual armar y probar la animación.
2. Fijar el FORMATO del archivo que después exportará el modelo en SimPy.
   La página web solo lee ese archivo y lo dibuja; no simula nada.

Uso (desde la raíz del proyecto):

    python src/demo_animacion.py

Escribe resultados/demo/demo_A.json, demo_B.json, demo_C.json y manifest.json.
Usa --salida para elegir otro destino sin modificar el motor.
Las tres estrategias reciben exactamente las mismas llegadas (misma semilla).

Unidades: metros y segundos. Coordenadas del plano: x hacia el este, y hacia
el norte, con la Séptima Avenida en x = 0, W30 en y = +40 y W29 en y = -40.
"""
import argparse
from exportacion_visual import exportar_corrida, exportar_manifiesto
import math
import random
from pathlib import Path

# ---------------------------------------------------------------- parámetros
SEMILLA = 20261113
DURACION = 720.0            # s simulados
DT = 0.5                    # paso de tiempo, s
V_LIBRE = 7.0               # m/s (≈ 25 km/h)
ACEL = 2.0                  # m/s²
FRENO = 3.0                 # m/s²
CICLO = 60.0
VERDE_AV, AMARILLO, TODO_ROJO = 28.0, 3.0, 2.0
VERDE_TR = 21.0
BRECHA_TIEMPO = 1.0         # s de separación adicional según la velocidad
CAJA = 8.0                  # m entre la línea de alto y el centro del cruce
OBSTRUCCION = {"t_inicio": 90.0, "t_fin": 390.0, "s": 64.0, "intervalo_paso": 12.0}
DEMANDA_VPH = {"N": 540, "W30O": 300, "W29E": 330}
UMBRAL_ALTO, UMBRAL_BAJO = 8, 5      # estrategia C: activar / soltar regulación
CAPACIDAD_TRAMO = 11
DESFASE_W29 = {"A": 40.0, "B": 12.0, "C": 12.0}
NOMBRES = {
    "A": "Tiempos fijos independientes",
    "B": "Tiempos fijos coordinados",
    "C": "Coordinación + regulación por ocupación",
}
LARGO = {"auto": 4.5, "camion": 7.5, "bus": 10.0}
SEPARACION = 2.5

# ------------------------------------------------------------------- la red
ENLACES = {  # nombre: (inicio, fin)
    "N": ((0, 140), (0, 40)),        # Séptima, al norte de W30
    "T": ((0, 40), (0, -40)),        # tramo interno W30 → W29
    "S": ((0, -40), (0, -140)),      # Séptima, al sur de W29
    "W30O": ((-140, 40), (0, 40)),   # W30, llegando desde el oeste
    "W30E": ((0, 40), (140, 40)),    # W30, saliendo hacia el este
    "W29E": ((140, -40), (0, -40)),  # W29, llegando desde el este
    "W29O": ((0, -40), (-140, -40)), # W29, saliendo hacia el oeste
}
LONGITUD = {k: math.dist(a, b) for k, (a, b) in ENLACES.items()}
SENAL = {"N": ("W30", "av"), "W30O": ("W30", "tr"), "T": ("W29", "av"), "W29E": ("W29", "tr")}
RUTAS = {
    "R1": ["N", "T", "S"],        # Séptima, recto
    "R2": ["N", "W30E"],          # Séptima → gira a W30
    "R3": ["W30O", "W30E"],       # W30, recto
    "R4": ["W30O", "T", "S"],     # W30 → gira a la Séptima (entra al tramo)
    "R5": ["W29E", "W29O"],       # W29, recto
    "R6": ["W29E", "S"],          # W29 → gira a la Séptima
    "R7": ["N", "T", "W29O"],     # Séptima → gira a W29
    "R8": ["W30O", "T", "W29O"],  # W30 → tramo → W29
}
ORDEN = ["S", "W30E", "W29O", "T", "N", "W30O", "W29E"]  # de aguas abajo a aguas arriba


def puntos_ruta(ruta):
    pts = [list(ENLACES[ruta[0]][0])]
    for e in ruta:
        pts.append(list(ENLACES[e][1]))
    return pts


def plan(t, desfase):
    """Estado del plan fijo: (avenida, transversal), cada uno 'V', 'A' o 'R'."""
    tau = (t - desfase) % CICLO
    av = "V" if tau < VERDE_AV else ("A" if tau < VERDE_AV + AMARILLO else "R")
    ini_tr = VERDE_AV + AMARILLO + TODO_ROJO
    tr = "V" if ini_tr <= tau < ini_tr + VERDE_TR else ("A" if ini_tr + VERDE_TR <= tau < ini_tr + VERDE_TR + AMARILLO else "R")
    return av, tr


def generar_llegadas(rng):
    """Llegadas de Poisson por acceso; iguales para las tres estrategias."""
    llegadas = []
    for acceso, vph in DEMANDA_VPH.items():
        t = 0.0
        while True:
            t += rng.expovariate(vph / 3600.0)
            if t >= DURACION - 60:      # el último minuto es para vaciar la escena
                break
            u = rng.random()
            if acceso == "N":
                ruta = "R2" if u > 0.85 else ("R7" if u > 0.68 else "R1")
            elif acceso == "W30O":
                ruta = "R3" if u > 0.30 else ("R8" if u > 0.24 else "R4")
            else:
                ruta = "R6" if u > 0.75 else "R5"
            v = rng.random()
            tipo = "bus" if v < 0.04 else ("camion" if v < 0.10 else "auto")
            llegadas.append({"t": round(t, 1), "acceso": acceso, "ruta": ruta, "tipo": tipo, "color": rng.randrange(6)})
    llegadas.sort(key=lambda a: a["t"])
    for i, a in enumerate(llegadas, 1):
        a["id"] = i
    return llegadas


def almacen_libre(carros, enlace):
    """Metros disponibles para guardar carros detenidos en un enlace.

    Va desde la entrada hasta la cola detenida (o hasta la línea de alto si
    nadie está detenido), menos el espacio que ocuparán los carros que aún se
    mueven. Es la regla de "no bloquear el cruce": solo entra quien cabe.
    """
    fin = LONGITUD[enlace] - (CAJA if enlace in SENAL else 0.0)
    en_movimiento = 0.0
    for c in carros:                      # del de adelante hacia atrás
        if c.v < 0.5:
            fin = c.s - c.esp
            en_movimiento = 0.0
        else:
            en_movimiento += c.esp
    return fin - en_movimiento


class Carro:
    __slots__ = ("id", "tipo", "color", "ruta", "i", "s", "v", "esp", "base", "k", "vk", "comprometido", "pase")

    def __init__(self, a):
        self.id, self.tipo, self.color, self.ruta = a["id"], a["tipo"], a["color"], a["ruta"]
        self.i, self.s, self.v = 0, 0.0, V_LIBRE
        self.esp = LARGO[self.tipo] + SEPARACION
        self.base = 0.0           # distancia de ruta acumulada antes del enlace actual
        self.k, self.vk = [], None
        self.comprometido = False
        self.pase = False

    def enlace(self):
        return RUTAS[self.ruta][self.i]

    def siguiente(self):
        r = RUTAS[self.ruta]
        return r[self.i + 1] if self.i + 1 < len(r) else None

    def marcar(self, t):
        """Guarda un punto (t, distancia en la ruta) solo cuando cambia la velocidad."""
        p = [round(t, 1), round(self.base + self.s, 2)]
        if len(self.k) >= 2:
            v = (p[1] - self.k[-1][1]) / max(p[0] - self.k[-1][0], 1e-9)
            if self.vk is not None and abs(v - self.vk) < 0.06:
                self.k[-1] = p
                return
            self.vk = v
        elif len(self.k) == 1:
            self.vk = (p[1] - self.k[0][1]) / max(p[0] - self.k[0][0], 1e-9)
        self.k.append(p)


def simular(estrategia, llegadas):
    en = {k: [] for k in ENLACES}                 # carros por enlace, el de adelante primero
    reserva = {k: 0.0 for k in ENLACES}           # espacio apartado por carros que ya cruzan
    espera = {k: [] for k in DEMANDA_VPH}         # carros que aún no caben en la escena
    pendientes = list(llegadas)
    terminados = []
    semaforos = {"W30": [], "W29": []}
    regulacion, regulando, t_cambio_reg = [], False, -99.0
    ultimo_paso_obst = -99.0
    m = {"t": [], "ocupacion_tramo": [], "verde_perdido": [], "salidas_tramo": [], "cola_norte": [], "fuera_de_escena": []}
    verde_perdido, salidas_tramo, t_bloqueo = 0.0, 0, None

    pasos = int(DURACION / DT)
    for n in range(pasos + 1):
        t = n * DT
        # --- semáforos ---
        ocup = len(en["T"])
        if estrategia == "C":
            if not regulando and ocup >= UMBRAL_ALTO:
                regulando, t_cambio_reg = True, t
                regulacion.append([t, 1])
            elif regulando and ocup <= UMBRAL_BAJO:
                regulando, t_cambio_reg = False, t
                regulacion.append([t, 0])
        est = {"W30": plan(t, 0.0), "W29": plan(t, DESFASE_W29[estrategia])}
        if estrategia == "C":
            av, tr = est["W30"]
            if regulando:
                est["W30"] = ("R", "V" if t - t_cambio_reg >= TODO_ROJO else "R")
            elif t - t_cambio_reg < TODO_ROJO and av != "R":
                est["W30"] = ("R", "R")
        for nodo, (av, tr) in est.items():
            if not semaforos[nodo] or semaforos[nodo][-1][1:] != [av, tr]:
                semaforos[nodo].append([round(t, 1), av, tr])

        # --- entradas a la escena ---
        while pendientes and pendientes[0]["t"] <= t:
            a = pendientes.pop(0)
            espera[a["acceso"]].append(a)
        for acceso, cola in espera.items():
            if cola:
                ultimo = en[acceso][-1] if en[acceso] else None
                if ultimo is None or ultimo.s - ultimo.esp >= 8.0:
                    c = Carro(cola.pop(0))
                    c.marcar(t)
                    en[acceso].append(c)

        # --- movimiento ---
        bloqueo_w30 = False
        obst_activa = OBSTRUCCION["t_inicio"] <= t < OBSTRUCCION["t_fin"]
        for e in ORDEN:
            L = LONGITUD[e]
            alto = L - CAJA
            lider = None
            for c in list(en[e]):
                sig = c.siguiente()
                limite = math.inf
                if lider is not None:
                    limite = lider.s - lider.esp - BRECHA_TIEMPO * c.v
                elif sig is not None and c.comprometido and en[sig]:
                    cola_sig = en[sig][-1]
                    limite = L + cola_sig.s - cola_sig.esp - BRECHA_TIEMPO * c.v
                # decisión de cruzar la línea de alto
                if sig is not None and not c.comprometido:
                    cruza = False
                    if c.s >= alto - 10.0 and (lider is None or lider.comprometido):
                        verde = True
                        if e in SENAL:
                            nodo, fase = SENAL[e]
                            verde = est[nodo][0 if fase == "av" else 1] == "V"
                        if verde:
                            if almacen_libre(en[sig], sig) - reserva[sig] >= CAJA + c.esp:
                                cruza = True
                            elif c.s >= alto - 1.0 and sig == "T" and e in ("N", "W30O"):
                                bloqueo_w30 = True          # hay verde, pero no cabe en el tramo
                                if e == "N":
                                    verde_perdido += DT
                    if cruza:
                        c.comprometido = True
                        reserva[sig] += c.esp
                    else:
                        limite = min(limite, alto)
                # paso alternado junto al camión
                if e == "T" and obst_activa and not c.pase and c.s < OBSTRUCCION["s"]:
                    primero = lider is None or lider.s >= OBSTRUCCION["s"]
                    if primero and c.s >= OBSTRUCCION["s"] - 1.0 and t - ultimo_paso_obst >= OBSTRUCCION["intervalo_paso"]:
                        ultimo_paso_obst = t
                        c.pase = True
                    else:
                        limite = min(limite, OBSTRUCCION["s"] - 0.5)
                hueco = max(0.0, limite - c.s)
                v = min(V_LIBRE, c.v + ACEL * DT, math.sqrt(2 * FRENO * hueco))
                avance = min(v * DT, hueco)
                c.v = avance / DT
                c.s += avance
                if c.s >= L:
                    en[e].remove(c)
                    if sig is None:
                        c.s = L
                        c.marcar(t + DT)
                        terminados.append(c)
                        if "T" in RUTAS[c.ruta]:
                            salidas_tramo += 1
                        continue
                    c.base += L
                    c.s -= L
                    c.i += 1
                    c.comprometido = False
                    c.pase = False
                    reserva[sig] -= c.esp
                    en[sig].append(c)
                    c.marcar(t + DT)
                    continue
                c.marcar(t + DT)
                lider = c
        if bloqueo_w30 and t_bloqueo is None:
            t_bloqueo = t

        # --- métricas, una vez por segundo ---
        if n % int(1 / DT) == 0:
            m["t"].append(int(t))
            m["ocupacion_tramo"].append(len(en["T"]))
            m["verde_perdido"].append(round(verde_perdido, 1))
            m["salidas_tramo"].append(salidas_tramo)
            m["cola_norte"].append(sum(1 for c in en["N"] if c.v < 0.5))
            m["fuera_de_escena"].append(sum(len(q) for q in espera.values()))

    vehiculos = terminados + [c for lista in en.values() for c in lista]
    vehiculos.sort(key=lambda c: c.id)
    ox, oy = 0, 40 - OBSTRUCCION["s"]
    return {
        "meta": {
            "es_demo": True,
            "aviso": "Datos de demostración generados por src/demo_animacion.py. No son resultados del proyecto.",
            "estrategia": estrategia,
            "nombre": NOMBRES[estrategia],
            "duracion": DURACION,
            "semilla": SEMILLA,
            "unidades": "metros y segundos; x al este, y al norte",
            "parametros": {
                "ciclo": CICLO, "verde_avenida": VERDE_AV, "verde_transversal": VERDE_TR,
                "desfase_w30": 0.0, "desfase_w29": DESFASE_W29[estrategia],
                "demanda_vph": DEMANDA_VPH, "velocidad_libre": V_LIBRE,
                "umbrales_regulacion": [UMBRAL_BAJO, UMBRAL_ALTO] if estrategia == "C" else None,
            },
        },
        "red": {
            "rutas": {r: puntos_ruta(e) for r, e in RUTAS.items()},
            "radio_giro": 6.0,
            "calles": [
                {"nombre": "Seventh Ave", "de": [0, 140], "a": [0, -140], "ancho": 9},
                {"nombre": "W 30th St", "de": [-140, 40], "a": [140, 40], "ancho": 8},
                {"nombre": "W 29th St", "de": [140, -40], "a": [-140, -40], "ancho": 8},
            ],
            "nodos": {"W30": [0, 40], "W29": [0, -40]},
            "lineas_alto": [
                {"nodo": "W30", "fase": "av", "x": 0, "y": 40 + CAJA, "a_lo_largo": "x"},
                {"nodo": "W30", "fase": "tr", "x": -CAJA, "y": 40, "a_lo_largo": "y"},
                {"nodo": "W29", "fase": "av", "x": 0, "y": -40 + CAJA, "a_lo_largo": "x"},
                {"nodo": "W29", "fase": "tr", "x": CAJA, "y": -40, "a_lo_largo": "y"},
            ],
            "tramo": {"de": [0, 40 - CAJA], "a": [0, -40 + CAJA], "capacidad": CAPACIDAD_TRAMO},
        },
        "obstruccion": {"t_inicio": OBSTRUCCION["t_inicio"], "t_fin": OBSTRUCCION["t_fin"], "x": ox, "y": oy - 6, "lado": -3.4, "intervalo_paso_s": OBSTRUCCION["intervalo_paso"]},
        "semaforos": semaforos,
        "regulacion": regulacion,
        "vehiculos": [{"id": c.id, "tipo": c.tipo, "color": c.color, "ruta": c.ruta, "k": c.k} for c in vehiculos],
        "metricas": m,
        "resumen": {
            "t_cola_llega_w30": t_bloqueo,
            "verde_perdido": round(verde_perdido, 1),
            "salidas_tramo": salidas_tramo,
            "ocupacion_maxima": max(m["ocupacion_tramo"]),
        },
    }


def main():
    raiz = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Exporta corridas de demostración con contrato v1")
    parser.add_argument('--salida', type=Path, default=raiz / 'resultados' / 'demo')
    salida = parser.parse_args().salida
    salida.mkdir(parents=True, exist_ok=True)
    llegadas = generar_llegadas(random.Random(SEMILLA))
    print(f"Llegadas generadas: {len(llegadas)} (iguales para A, B y C)")
    escenarios = []
    for estrategia in "ABC":
        datos = simular(estrategia, llegadas)
        archivo = salida / f"demo_{estrategia}.json"
        exportar_corrida(datos, archivo, motor='demo_animacion', entradas_id=f'demo-{SEMILLA}')
        escenarios.append({'id': estrategia, 'archivo': archivo.name})
        r = datos["resumen"]
        print(f"  {estrategia}: cola llega a W30 en t={r['t_cola_llega_w30']} s | verde perdido {r['verde_perdido']} s | "
              f"salidas por el tramo {r['salidas_tramo']} | ocupación máx. {r['ocupacion_maxima']} | {archivo.stat().st_size // 1024} KB")
    exportar_manifiesto(escenarios, salida / 'manifest.json')


if __name__ == "__main__":
    main()
