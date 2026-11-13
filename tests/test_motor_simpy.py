"""Verificaciones del motor SimPy: conservación, cotas, Little y Webster."""
import sys
import unittest
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'src'))
from motor_simpy import (Parametros, simular, llegadas_constantes, llegadas_poisson,
                         verificar_conservacion, verificar_little, webster)


def demanda_pico():
    iv = pd.read_csv(RAIZ / 'datos/procesados/intervalos.csv')
    return llegadas_poisson(iv, '2026-03-04', '17:00', '18:00', semilla=7)


class MotorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ll = demanda_pico()
        cls.r = {e: simular(Parametros(estrategia=e, obstr_inicio=900, obstr_dur=900), cls.ll, 4800) for e in 'ABC'}

    def test_conservacion_y_cotas(self):
        for e, r in self.r.items():
            with self.subTest(estrategia=e):
                self.assertTrue(verificar_conservacion(r))

    def test_obstruccion_no_borra_vehiculos(self):
        for e, r in self.r.items():
            with self.subTest(estrategia=e):
                self.assertEqual(r.veh['t_salida'].notna().sum(), len(self.ll))

    def test_little_en_el_tramo(self):
        self.assertLess(verificar_little(self.r['A'])['error_rel'], 0.05)

    def test_webster_acceso_aislado(self):
        p = Parametros()
        r = simular(p, llegadas_constantes('W29E', 500, 36000, semilla=1), 37000)
        simulada = r.tiempos()['espera'].mean()
        self.assertAlmostEqual(simulada / webster(500, p), 1, delta=0.15)

    def test_coordinacion_reduce_espera_sin_obstruccion(self):
        a = simular(Parametros(estrategia='A'), self.ll, 4800).metricas()
        b = simular(Parametros(estrategia='B'), self.ll, 4800).metricas()
        self.assertLess(b['espera_N_s'], a['espera_N_s'])

    def test_misma_demanda_en_las_tres(self):
        n = {e: len(r.veh) for e, r in self.r.items()}
        self.assertEqual(len(set(n.values())), 1)


if __name__ == '__main__':
    unittest.main()
