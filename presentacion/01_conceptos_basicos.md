# Conceptos básicos

## Dato

Un dato es un valor que registramos sobre algo que nos interesa estudiar.

**En este proyecto:** 30 vehículos que llegan a W29 y Seventh Avenue entre las 8:00 y las 8:15. Es un ejemplo ficticio, no un conteo real.

## Acceso

Un acceso es una entrada por la que los vehículos llegan a una intersección. Se distingue por la calle y el sentido de circulación.

**Ejemplo:** vehículos que avanzan hacia el oeste por W29, desde Sixth Avenue, y llegan a Seventh Avenue. Es uno de varios accesos al cruce.

## Intervalo de conteo

Es el periodo durante el cual sumamos los vehículos que llegan por un acceso.

**Ejemplo:** 8:00–8:15 es un intervalo de 15 minutos. El número registrado resume ese intervalo; no describe cuándo llegó cada vehículo.

## Tasa

La tasa expresa cuántos vehículos llegan por unidad de tiempo. Se calcula como conteo dividido entre duración.

**Ejemplo didáctico:** 30 vehículos ÷ 15 minutos = 2 vehículos por minuto = 120 vehículos por hora, como promedio equivalente. No significa que lleguen exactamente dos en cada minuto.

## Simulación

Una simulación representa cómo cambia un sistema con el tiempo según reglas definidas.

**En este proyecto:** representar llegadas, semáforos, salidas y colas en dos intersecciones para comparar coordinación sin cambiar la demanda ni el bloqueo.

## Límite de interpretación

Los conteos históricos son incompletos para los accesos seleccionados. Usaremos algunos como referencia y declararemos los demás valores como supuestos ficticios. El resultado describe el modelo bajo esos supuestos; por sí solo no demuestra qué ocurre en Nueva York.

Consulta el [diagrama de los accesos](02_red_y_accesos.md) para ver de dónde llegan y hacia dónde viajan.
