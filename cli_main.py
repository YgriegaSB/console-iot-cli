#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Console IoT CLI
Una herramienta de línea de comandos para comunicación serial.
"""

import sys
import argparse
import serial
import serial.tools.list_ports
import threading
import time
import datetime
import os
import queue
from typing import Optional

# Configuración de colores para la terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        Colors.HEADER = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.GREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''

class Logger:
    def __init__(self, filename: str = "session_log.txt"):
        self.log_dir = "logs_iot"
        self.base_filename = filename
        self.filepath = os.path.join(self.log_dir, os.path.basename(filename))
        self.initialized = False

    def _initialize_log(self):
        if not os.path.exists(self.log_dir):
            try:
                os.makedirs(self.log_dir)
            except Exception as e:
                print(f"{Colors.FAIL}Error creando directorio de logs: {e}{Colors.ENDC}")
                return

        if not self.initialized:
            try:
                mode = 'a' if os.path.exists(self.filepath) else 'w'
                with open(self.filepath, mode, encoding='utf-8') as f:
                    f.write(f"--- Log Session Started: {datetime.datetime.now()} ---\n")
                self.initialized = True
            except Exception as e:
                print(f"{Colors.FAIL}Error iniciando archivo de log: {e}{Colors.ENDC}")

    def log(self, message: str, msg_type: str = "INFO"):
        if not self.initialized:
            self._initialize_log()

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_msg = f"[{timestamp}] [{msg_type}] {message}"
        
        try:
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write(formatted_msg + "\n")
        except Exception as e:
            print(f"{Colors.FAIL}Error escribiendo al log: {e}{Colors.ENDC}")

class SerialHandler:
    def __init__(self, port: str, baudrate: int, logger: Logger, headless: bool = False):
        self.port = port
        self.baudrate = baudrate
        self.logger = logger
        self.headless = headless
        self.serial_conn: Optional[serial.Serial] = None
        self.is_connected = False
        self.stop_event = threading.Event()
        self.read_thread: Optional[threading.Thread] = None
        self.rx_queue = queue.Queue()

    def connect(self) -> bool:
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            self.is_connected = True
            self.stop_event.clear()
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            msg = f"Conectado a {self.port} a {self.baudrate} baudios."
            self.logger.log(msg, "SYS")
            if not self.headless:
                print(f"{Colors.GREEN}{msg}{Colors.ENDC}")
            return True
        except Exception as e:
            msg = f"Error conectando a {self.port}: {e}"
            self.logger.log(msg, "ERROR")
            if not self.headless:
                print(f"{Colors.FAIL}{msg}{Colors.ENDC}")
            return False

    def disconnect(self):
        if self.is_connected:
            self.stop_event.set()
            if self.read_thread:
                self.read_thread.join(timeout=1.0)
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
            self.is_connected = False
            msg = "Desconectado."
            self.logger.log(msg, "SYS")
            if not self.headless:
                print(f"{Colors.WARNING}{msg}{Colors.ENDC}")

    def send(self, data: str):
        if not self.is_connected or not self.serial_conn:
            print(f"{Colors.FAIL}No hay conexión establecida.{Colors.ENDC}")
            return

        try:
            # Agregar terminador por defecto \n si no se especifica otro (simple implementation)
            if not data.endswith(('\n', '\r')):
                data += '\n'
            
            self.serial_conn.write(data.encode('utf-8'))
            self.logger.log(data.strip(), "TX")
            if not self.headless:
                # Opcional: mostrar lo que enviamos? Generalmente sí.
                # print(f"{Colors.BLUE}TX > {data.strip()}{Colors.ENDC}")
                pass 
        except Exception as e:
            msg = f"Error enviando datos: {e}"
            self.logger.log(msg, "ERROR")
            if not self.headless:
                print(f"{Colors.FAIL}{msg}{Colors.ENDC}")

    def _read_loop(self):
        while not self.stop_event.is_set() and self.serial_conn and self.serial_conn.is_open:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        self.logger.log(line, "RX")
                        if not self.headless:
                            print(f"{line}") # Imprimir directo como pide el usuario, o con color?
                            # El usuario dijo: "Los mensajes recibidos aparecen en negro" (default terminal)
                            # Vamos a dejarlo default o cyan para distinguir.
                            # print(f"{Colors.CYAN}{line}{Colors.ENDC}")
            except Exception as e:
                self.logger.log(f"Error de lectura: {e}", "ERROR")
                break
            time.sleep(0.01)

def list_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No se encontraron puertos COM.")
    else:
        print(f"{Colors.HEADER}Puertos disponibles:{Colors.ENDC}")
        for p in ports:
            print(f"  - {p.device}: {p.description}")

def print_help():
    help_text = f"""
{Colors.HEADER}Console IoT CLI - Manual de Uso{Colors.ENDC}

{Colors.BOLD}MODO INTERACTIVO:{Colors.ENDC}
  Escribe cualquier texto y presiona ENTER para enviarlo al puerto serial.

{Colors.BOLD}COMANDOS ESPECIALES:{Colors.ENDC}
  {Colors.BOLD}/exit{Colors.ENDC}      : Salir de la aplicación.
  {Colors.BOLD}/help{Colors.ENDC}      : Mostrar este mensaje de ayuda.
  {Colors.BOLD}/list{Colors.ENDC}      : Listar puertos COM disponibles.
  {Colors.BOLD}/connect [port] [baud]{Colors.ENDC} : Conectar a un puerto (ej: /connect COM3 115200).
  {Colors.BOLD}/disconnect{Colors.ENDC}: Desconectar del puerto actual.
  {Colors.BOLD}/clear{Colors.ENDC}     : Limpiar la pantalla de la terminal.

{Colors.BOLD}ARGUMENTOS DE INICIO:{Colors.ENDC}
  --port PORT       : Puerto serial para conectar automáticamente al inicio.
  --baud BAUDRATE   : Velocidad en baudios (default: 115200).
  --headless        : Modo sin salida por pantalla (solo log).
  --log FILE        : Archivo de log personalizado (default: session_log.txt).
    """
    print(help_text)

def main():
    parser = argparse.ArgumentParser(description="Console IoT CLI")
    parser.add_argument("--port", help="Puerto COM para conectar automáticamente")
    parser.add_argument("--baud", type=int, default=115200, help="Baudrate (default: 115200)")
    parser.add_argument("--headless", action="store_true", help="Ejecutar sin salida por consola (solo log)")
    parser.add_argument("--log", default="session_log.txt", help="Ruta del archivo de log")
    
    args = parser.parse_args()

    if args.headless:
        Colors.disable()

    logger = Logger(args.log)
    
    if not args.headless:
        print(f"{Colors.HEADER}=== Console IoT CLI ==={Colors.ENDC}")
        print("Escribe '/help' para ver los comandos disponibles.")

    serial_handler = None
    
    # Auto-conexión si se proveen argumentos
    if args.port:
        serial_handler = SerialHandler(args.port, args.baud, logger, args.headless)
        if not serial_handler.connect():
            serial_handler = None

    try:
        while True:
            try:
                # En modo headless, si ya estamos conectados, solo esperamos (loop infinito)
                # Si no estamos conectados en headless, no tiene mucho sentido, pero permitimos input ciego?
                # Mejor: si es headless, bloqueamos en un loop de espera para no consumir CPU si no hay input user.
                # Pero el usuario pidió headless para "ver que se ejecuta pero no se muestran los logs".
                # Asumimos que headless podría querer enviar comandos ciegamente o simplemente loggear.
                
                if args.headless:
                    # En modo headless puro, probablemente solo queremos loggear lo que llega.
                    # Si el usuario quiere input, no sería headless total.
                    # Simplemente dormimos y dejamos que el thread de lectura haga su trabajo.
                    time.sleep(1)
                    continue

                # Modo interactivo normal
                user_input = input() # Bloqueante
                
                if not user_input.strip():
                    continue

                if user_input.startswith('/'):
                    parts = user_input.split()
                    cmd = parts[0].lower()

                    if cmd == '/exit':
                        break
                    elif cmd == '/help':
                        print_help()
                    elif cmd == '/list':
                        list_ports()
                    elif cmd == '/clear':
                        os.system('cls' if os.name == 'nt' else 'clear')
                    elif cmd == '/disconnect':
                        if serial_handler:
                            serial_handler.disconnect()
                            serial_handler = None
                        else:
                            print("No hay conexión activa.")
                    elif cmd == '/connect':
                        if len(parts) < 2:
                            print("Uso: /connect [puerto] [baudrate opcional]")
                            continue
                        
                        port = parts[1]
                        baud = int(parts[2]) if len(parts) > 2 else 115200
                        
                        if serial_handler:
                            serial_handler.disconnect()
                        
                        serial_handler = SerialHandler(port, baud, logger, args.headless)
                        serial_handler.connect()
                    else:
                        print(f"Comando desconocido: {cmd}")
                else:
                    # Enviar datos raw
                    if serial_handler and serial_handler.is_connected:
                        serial_handler.send(user_input)
                    else:
                        print(f"{Colors.WARNING}No estás conectado. Usa /connect o /list.{Colors.ENDC}")

            except KeyboardInterrupt:
                break
            except EOFError:
                break

    finally:
        if serial_handler:
            serial_handler.disconnect()
        if not args.headless:
            print("\nSaliendo...")

if __name__ == "__main__":
    main()
