# Coordinación semafórica y propagación del congestionamiento

Evaluar si la coordinación semafórica ayuda a contener la propagación del congestionamiento ante un bloqueo. La capacidad del tramo bloqueado es una restricción del modelo.

## Organización

```text
notebooks/          01 datos → 02 simulación → 03 resultados
src/                Código reutilizable de Python cuando sea necesario
datos/             (ver carpetas siguientes)
  originales/       Datos de entrada sin modificar
  procesados/       Datos limpios o derivados
  fuentes.csv       Procedencia, unidades y fecha de cada conjunto
guias/              Requisitos y tesis de referencia (solo local)
escenarios/         Parámetros de los experimentos
resultados/         Una carpeta por corrida: parámetros, métricas y figuras
docs/bitacora.md     Decisiones y avances en pocas líneas
```

## Empezar

Usar Python 3.13 aislado con `uv` (disponible en este equipo).

```bash
uv venv --python 3.13 --managed-python --seed .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyterlab
```

En Windows, activar con `.venv\Scripts\activate`. Seleccionar el entorno `.venv` como kernel y abrir `notebooks/01_datos.ipynb`.

## Comparación prevista

- Comparar semáforos sin coordinación frente a coordinación definida explícitamente.
- Mantener iguales demanda, red, bloqueo y semillas entre escenarios comparables.
- Representar almacenamiento finito y bloqueo aguas arriba por colas (spillback).
- Medir alcance de la cola, tiempo hasta afectar otra intersección, demora y vehículos que completan el recorrido.
- Registrar también colas retenidas en accesos para detectar si solo se desplaza el congestionamiento.
- Definir unidades, horizonte, réplicas y supuestos antes de interpretar resultados.

## Guardar sin acumular documentos

- Notebooks: pregunta, código, resultado y conclusión breve.
- Bitácora: fecha, decisión y siguiente paso; máximo tres líneas por entrada.
- Corridas: `resultados/AAAAMMDD_HHMMSS_escenario/` con `parametros.json`, `metricas.csv`, `entorno.txt` y figuras. Guardar semilla y versiones (`python -m pip freeze`).
- Datos y resultados se conservan localmente por defecto; Git guarda código, escenarios y procedencia. Publicar conjuntos seleccionados de forma explícita.
- No modificar originales ni guardar copias llamadas `final_v2`.

Estado: auditorías cerradas. [Recomendación de ubicación](docs/decision_ubicacion.md): mantener W29–W30 con una base ficticia y supuestos explícitos. Evidencia: `notebooks/01_auditoria_datos_historicos.ipynb` y `notebooks/01b_auditoria_historico_complementario.ipynb`. Base ficticia generada en `notebooks/01_datos.ipynb` (semilla 20261112; 2,016 intervalos y 206,888 vehículos). Siguiente fase: análisis exploratorio; SimPy pendiente.

Para repetir la auditoría: completar `SOCRATA_APP_TOKEN` en `.env` y ejecutar el notebook de auditoría. El Secret Token no se utiliza; la evidencia se guarda localmente.

Aprendizaje y dudas: [bitácora de aprendizaje](docs/bitacora_aprendizaje.md). Cada paso se explicará antes de ejecutarse; el diccionario de variables se cerrará antes de generar datos.

Material breve para diapositivas: `presentacion/`. Solo guardar allí conceptos y resultados que se puedan presentar.
