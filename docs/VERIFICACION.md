# Informe de entrega y verificación

Fecha: 12 de noviembre de 2026. Proyecto local independiente, Sesión 14.

## Entorno verificado

- Python 3.13.17, entorno `.venv` con `sys.prefix != sys.base_prefix`.
- Flask 3.1.2 y Waitress 3.0.2 instalados en el entorno del proyecto.
- `pip check`: sin dependencias incompatibles.
- JavaScript puro, HTML, CSS y Canvas; sin recursos externos de interfaz.
- Ningún repositorio remoto ni servicio Render creado o modificado.

## Pruebas ejecutadas

**75 pruebas unittest aprobadas; cero fallos.** La última ejecución completó la suite en aproximadamente 0.44 segundos.

| Archivo | Pruebas | Cobertura principal |
| --- | ---: | --- |
| test_euler.py | 10 | Resultado, trazas, fracciones exactas, soluciones conocidas y orden 1 |
| test_heun.py | 12 | Predictores, correctores, Decimal a 60 dígitos, diferencia con punto medio y orden 2 |
| test_problema.py | 18 | Solución exacta, errores, identidad conservada, ramas negativas, dominio y cálculo de 10 000 pasos |
| test_validaciones.py | 19 | Tipos, booleanos, infinitos, pasos, singularidades, escala y límite de iteraciones |
| test_app.py | 16 | Página, API, errores JSON, métodos HTTP, archivos estáticos, salud y cabeceras |

También se ejecutaron `compileall`, `node --check` y `pip check`, sin errores. El archivo `render.yaml` se validó con PyYAML y JSON Schema Draft 2020-12 contra el esquema oficial descargado de Render. Los validadores se instalaron solamente en `tmp/validation`, excluido de publicación; no son dependencias de la aplicación. No se realizó validación remota de disponibilidad de recursos o planes.

## Resultados calculados

Constante: C = 3.5. Solución exacta: y(1.2) = 1.7749804380768697.

| Método | Aproximación | Error absoluto | Error relativo (%) |
| --- | ---: | ---: | ---: |
| Euler | 1.7412776412776414 | 0.033702796799228274 | 1.8987700414177011 |
| Heun | 1.775806670950786 | 0.000826232873916366 | 0.04654884393044697 |

Primera iteración: Euler = 1.85; predictor de Heun = 1.85; corrector = 1.8706388206388207.

Segunda iteración de Heun: predictor = 1.759384187290956; k1 = -1.1125463334786485; k2 = -0.7840966602820466; corrector = 1.775806670950786. La diferencia de los últimos dígitos de k2 respecto del texto de referencia se debe a la representación flotante del nodo, no a redondeo intermedio.

## Revisión de navegador realizada

- Carga automática del caso oficial y recursos locales.
- Inspección visual de la página completa en escritorio (1440 × 1000) y móvil (390 × 844).
- Gráfica Canvas con las tres series y controles para ocultar/mostrar Euler.
- Selector de la segunda iteración: predictor, pendientes y corrector correctos.
- Cambio de y0 a -2: resultado de Heun negativo correcto.
- Aviso de resultados desactualizados al modificar parámetros.
- h = 0: mensaje comprensible y resultados anteriores ocultos.
- Restauración de parámetros y recálculo del caso oficial.
- h = 0.005: 40 iteraciones y navegación de filas 1–20 a 21–40.
- Botón de copia: la interfaz confirmó la escritura al portapapeles. La API de lectura del navegador de pruebas devolvió un portapapeles vacío; por ello no se certificó el contenido mediante una lectura independiente. La descarga alternativa ante permisos denegados está implementada, pero no se forzó ese rechazo durante la revisión.
- Consola revisada: sin errores ni advertencias de JavaScript.
- Carga y cálculo final comprobados también con Waitress en loopback.

Capturas: [escritorio](desktop.jpg) y [móvil](mobile.jpg). Las tablas anchas tienen desplazamiento horizontal dentro de su contenedor en pantallas pequeñas.

## Incidencias y correcciones

1. La creación inicial de `.venv` fue bloqueada al escribir temporales de `ensurepip`. Se completó con la autorización de ejecución del sistema y se verificó Python 3.13.17 dentro del entorno.
2. La red restringida impidió descargar dependencias. La instalación autorizada desde PyPI finalizó correctamente.
3. El servidor iniciado dentro del aislamiento no era accesible al navegador. Se reinició con permisos de ejecución locales y se verificó el funcionamiento real.
4. En móvil, ocultar un salto de línea unía dos frases del texto introductorio. Se añadió el espacio correspondiente y se recargó la página para verificarlo.
5. Las pruebas matemáticas no detectaron errores en los algoritmos implementados.

La advertencia de ubicación de Python apareció en comandos dentro del entorno restringido, pero no impidió las pruebas ni el servidor autorizado. No se modificó la instalación global de Python.

## Inicio local

Desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe -m backend.app
```

Abrir http://127.0.0.1:5014. Para detener, Ctrl+C en la terminal. La vista previa de verificación se detuvo al finalizar; volver a ejecutar el comando inicia la aplicación.

## Pendientes para publicación

- Revisar la entrega con el estudiante y obtener autorización explícita antes de crear un repositorio o desplegar.
- Verificar nuevamente la disponibilidad del plan y la validación de plataforma de Render al publicar.
- Si el navegador bloquea el portapapeles, usar la descarga de texto alternativa y revisar su contenido en el navegador de uso habitual.
- La entrega manuscrita sigue siendo independiente del software.

La estructura completa, fórmulas, API y comandos reproducibles están documentados en el README en inglés.