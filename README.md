# Console IoT CLI

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![PySerial](https://img.shields.io/badge/pyserial-3.5-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by-nc-sa/4.0/)

Una herramienta de línea de comandos robusta para comunicación serial, diseñada como alternativa ligera a la versión con interfaz gráfica.

## Características

- **Interfaz de Línea de Comandos (CLI)**: Interacción directa y rápida.
- **Modo Headless**: Ejecución en segundo plano sin salida por pantalla, ideal para automatización.
- **Logging Automático**: Todas las sesiones se guardan en archivos de log con timestamps.
- **Detección de Puertos**: Listado automático de puertos COM disponibles.
- **Colores**: Salida formateada con colores para fácil lectura (desactivable).

## Instalación

1. Asegúrate de tener Python 3 instalado.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Instalación Global (Opcional)
Puedes instalar la herramienta en tu sistema para usarla desde cualquier lugar:
```bash
pip install .
```
Una vez instalado, podrás ejecutar el comando `console-iot` directamente:
```bash
console-iot --help
```

## Uso

### Modo Interactivo
Simplemente ejecuta el script:
```bash
python cli_main.py
```
Dentro de la aplicación, usa `/help` para ver los comandos disponibles.

### Conexión Directa
Puedes conectar directamente al iniciar:
```bash
python cli_main.py --port COM3 --baud 115200
```

### Modo Headless (Automatización)
Para ejecutar sin mostrar nada en la terminal (útil para scripts o tareas en segundo plano), pero manteniendo el guardado de logs:
```bash
python cli_main.py --port COM3 --headless
```

### Comandos Internos
- `/help`: Muestra la ayuda.
- `/list`: Lista los puertos COM.
- `/connect [port] [baud]`: Conecta a un puerto.
- `/disconnect`: Cierra la conexión actual.
- `/exit`: Sale de la aplicación.

## Estructura de Logs
Los logs se guardan por defecto en la carpeta `logs_iot/` (ej. `logs_iot/session_log.txt`).
Formato: `[FECHA HORA] [TIPO] Mensaje`
Tipos: `TX` (Enviado), `RX` (Recibido), `SYS` (Sistema), `ERROR`.

## Glosario de Conceptos

- **Baudrate (Tasa de Baudios)**: Velocidad de transmisión de datos en una conexión serial. Es fundamental que tanto el computador como el dispositivo utilicen la misma velocidad (ej. 9600, 115200) para entenderse.
- **Headless**: Modo de ejecución "sin cabeza" o sin interfaz visual. Permite correr la aplicación en segundo plano o en servidores donde no hay un monitor conectado, siendo ideal para automatización.
- **Puerto COM**: Designación de los puertos seriales en sistemas Windows (ej. COM3). Es la interfaz física o virtual a través de la cual se conecta el dispositivo IoT.

## Licencia

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

Este proyecto está licenciado bajo [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

**En resumen:**
- ✅ **Permitido**: Uso personal, educativo, modificación y distribución.
- ⚠️ **Requerido**: Atribución a **Nicolás Pinochet Flores** y compartir bajo la misma licencia.
- ❌ **Prohibido**: Uso comercial sin permiso explícito.

Para más detalles, consulta el archivo [`LICENSE`](LICENSE) o visita la [licencia completa](http://creativecommons.org/licenses/by-nc-sa/4.0/).

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
