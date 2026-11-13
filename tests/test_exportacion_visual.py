import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / 'src'))
from exportacion_visual import validar_corrida, exportar_corrida, exportar_manifiesto

EJEMPLO = json.loads((RAIZ / 'contratos/ejemplo_A.json').read_text())
CASOS = json.loads((RAIZ / 'contratos/casos_invalidos.json').read_text())


class ContratoVisualTest(unittest.TestCase):
    def test_casos_compartidos(self):
        validar_corrida(EJEMPLO)
        for caso in CASOS:
            with self.subTest(caso=caso['nombre']):
                datos = copy.deepcopy(EJEMPLO)
                destino = datos
                for campo in caso['ruta'][:-1]:
                    destino = destino[campo]
                destino[caso['ruta'][-1]] = caso['valor']
                with self.assertRaises(ValueError):
                    validar_corrida(datos)

    def test_exportar_no_muta_ni_sobrescribe_si_es_invalido(self):
        original = copy.deepcopy(EJEMPLO)
        with tempfile.TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / 'A.json'
            exportar_corrida(original, archivo, motor='prueba', entradas_id='fixture')
            self.assertEqual(original, EJEMPLO)
            contenido = archivo.read_bytes()
            original['version_contrato'] = '1.0'
            original['vehiculos'][0]['ruta'] = 'inexistente'
            with self.assertRaises(ValueError):
                exportar_corrida(original, archivo, motor='prueba', entradas_id='fixture')
            self.assertEqual(archivo.read_bytes(), contenido)

    def test_manifiesto_duplicado(self):
        with tempfile.TemporaryDirectory() as carpeta:
            with self.assertRaises(ValueError):
                exportar_manifiesto([{'id':'A','archivo':'A.json'}] * 3, Path(carpeta) / 'manifest.json')
