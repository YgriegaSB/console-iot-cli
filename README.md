# Console IoT CLI

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![PySerial](https://img.shields.io/badge/pyserial-3.5-green.svg)
![Version](https://img.shields.io/badge/version-2.0.0-orange.svg)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](http://creativecommons.org/licenses/by-nc-sa/4.0/)

Una herramienta de línea de comandos robusta y completa para comunicación serial, TCP y UDP, diseñada como alternativa a Hercules SETUP Utility.

## Características

### Protocolos Soportados
- **Serial (RS-232)**: Comunicación serial completa con control de flujo y líneas modem
- **TCP Client**: Conexión como cliente a servidores TCP
- **TCP Server**: Servidor TCP para recibir conexiones
- **UDP**: Comunicación UDP bidireccional

### Características Avanzadas
- **Hex View**: Visualización de datos en formato hexadecimal
- **Hex Input**: Envío de datos en formato hex usando prefijos `#` o `$`
- **Control de Flujo**: Soporte para RTS/CTS y XON/XOFF
- **Líneas Modem**: Control manual de RTS/DTR y monitoreo de CTS/DSR/RI/CD
- **Modo Headless**: Ejecución en segundo plano sin salida por pantalla
- **Logging Automático**: Todas las sesiones se guardan con timestamps
- **Colores**: Salida formateada con colores para fácil lectura

## Instalación

1. Asegúrate de tener Python 3 instalado.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

### Instalación Global (Recomendado)
Instala la herramienta en tu sistema para usarla desde cualquier lugar:
```bash
pip install .
```
Una vez instalado, podrás ejecutar el comando `console-iot` directamente:
```bash
console-iot --help
```

## Uso

### Modo Interactivo
Ejecuta el programa sin argumentos para entrar en modo interactivo:
```bash
console-iot
```

### Conexión Automática al Inicio
```bash
# Serial
console-iot --port COM3 --baud 115200

# Modo Headless (sin salida por pantalla)
console-iot --port COM3 --headless
```

## Comandos

### Conexión

#### Serial
```bash
# Conexión básica (usa defaults: 8N1)
/connect serial [port] [baud]

# Con parámetros opcionales
/connect serial [port] [baud] [--data 5|6|7|8] [--parity N|E|O|M|S] [--stopbits 1|1.5|2] [--rtscts] [--xonxoff]

# Ejemplos:
/connect serial COM3 115200                           # 8N1 (default)
/connect serial COM3 9600 --data 7 --parity E         # 7E1
/connect serial COM3 19200 --parity O --stopbits 2    # 8O2
/connect serial COM3 115200 --rtscts                  # 8N1 con RTS/CTS
```

#### TCP/UDP
```bash
/connect tcp [host] [port]                             # Conectar como cliente TCP
/listen tcp [port]                                     # Iniciar servidor TCP
/udp [local_port] [remote_host] [remote_port]         # Modo UDP
/disconnect                                            # Cerrar conexión actual
```

### Control Serial Avanzado
```bash
/rts [on|off]     # Controlar línea RTS
/dtr [on|off]     # Controlar línea DTR
/status           # Ver estado de líneas modem (CTS, DSR, RI, CD)
```

### Visualización
```bash
/view hex         # Cambiar a vista hexadecimal
/view ascii       # Cambiar a vista ASCII (por defecto)
```

### General
```bash
/list             # Listar puertos COM disponibles
/clear            # Limpiar pantalla
/help             # Mostrar ayuda
/exit             # Salir
```

### Envío de Datos

**Modo ASCII (por defecto):**
```
Hola Mundo
```

**Modo Hexadecimal:**
```
#48656C6C6F        # Usando prefijo #
$48656C6C6F        # Usando prefijo $
```

## Ejemplos de Uso

### Serial Básico (8N1)
```bash
console-iot
/connect serial COM3 115200
Hola desde serial
/disconnect
```

### Serial con Configuración Personalizada (7E1)
```bash
console-iot
/connect serial COM3 9600 --data 7 --parity E --stopbits 1
# Útil para protocolos antiguos o equipos industriales
/status
/disconnect
```

### Serial con Control de Flujo
```bash
console-iot
/connect serial COM3 115200 --rtscts
/status
Hola desde serial
/disconnect
```

### Cliente TCP
```bash
console-iot
/connect tcp 192.168.1.100 23
GET / HTTP/1.1
/disconnect
```

### Servidor TCP
```bash
console-iot
/listen tcp 8080
# Espera conexiones en puerto 8080
```

### UDP
```bash
console-iot
/udp 5000 192.168.1.100 5001
# Escucha en puerto 5000, envía a 192.168.1.100:5001
```

### Visualización Hexadecimal
```bash
console-iot --port COM3
/view hex
# Ahora todos los datos recibidos se muestran en hexadecimal
#0D0A              # Enviar CRLF en hex
/view ascii       # Volver a modo ASCII
```

## Estructura de Logs
Los logs se guardan automáticamente en `logs_iot/session_log.txt`.

**Formato:** `[FECHA HORA] [TIPO] Mensaje`

**Tipos:**
- `TX`: Datos enviados
- `RX`: Datos recibidos
- `SYS`: Eventos del sistema
- `ERROR`: Errores

## Arquitectura del Proyecto

```
console-iot-cli/
├── console_iot/              # Paquete principal
│   ├── __init__.py
│   ├── main.py               # Punto de entrada
│   ├── utils/                # Utilidades
│   │   ├── colors.py         # Colores para terminal
│   │   └── logger.py         # Sistema de logging
│   └── connections/          # Manejadores de conexión
│       ├── base.py           # Clase base abstracta
│       ├── serial_conn.py    # Conexión serial
│       ├── tcp_conn.py       # TCP Client/Server
│       └── udp_conn.py       # UDP
├── setup.py                  # Configuración de instalación
├── requirements.txt          # Dependencias
└── README.md                 # Este archivo
```

## Licencia

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

Este proyecto está licenciado bajo [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

**En resumen:**
- ✅ **Permitido**: Uso personal, educativo, modificación y distribución.
- ⚠️ **Requerido**: Atribución a **Nicolás Pinochet** y compartir bajo la misma licencia.
- ❌ **Prohibido**: Uso comercial sin permiso explícito.

Para más detalles, consulta el archivo [`LICENSE`](LICENSE) o visita la [licencia completa](http://creativecommons.org/licenses/by-nc-sa/4.0/).

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
