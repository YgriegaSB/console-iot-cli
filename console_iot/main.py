import argparse
import time
import os
import sys
from .utils.logger import Logger
from .utils.colors import Colors
from .connections.serial_conn import SerialConnection, list_available_ports
from .connections.tcp_conn import TCPClientConnection, TCPServerConnection
from .connections.udp_conn import UDPConnection

def print_help():
    help_text = f"""
{Colors.HEADER}Console IoT CLI - Manual de Uso{Colors.ENDC}

{Colors.BOLD}MODO INTERACTIVO:{Colors.ENDC}
  Escribe cualquier texto y presiona ENTER para enviarlo.

{Colors.BOLD}COMANDOS DE CONEXIÓN:{Colors.ENDC}
  {Colors.BOLD}/connect serial [port] [baud]{Colors.ENDC} : Conectar a puerto serial (ej: /connect serial COM3 115200).
  {Colors.BOLD}/connect tcp [host] [port]{Colors.ENDC}    : Conectar como Cliente TCP (ej: /connect tcp 192.168.1.10 23).
  {Colors.BOLD}/listen tcp [port]{Colors.ENDC}            : Iniciar Servidor TCP (ej: /listen tcp 8080).
  {Colors.BOLD}/udp [local_port] [remote_host] [remote_port]{Colors.ENDC} : Iniciar modo UDP.

{Colors.BOLD}COMANDOS GENERALES:{Colors.ENDC}
  {Colors.BOLD}/list{Colors.ENDC}       : Listar puertos COM disponibles.
  {Colors.BOLD}/disconnect{Colors.ENDC} : Cerrar la conexión actual.
  {Colors.BOLD}/clear{Colors.ENDC}      : Limpiar pantalla.
  {Colors.BOLD}/exit{Colors.ENDC}       : Salir.
  {Colors.BOLD}/help{Colors.ENDC}       : Mostrar ayuda.

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

    connection = None
    
    # Auto-conexión si se proveen argumentos (Serial por defecto)
    if args.port:
        connection = SerialConnection(args.port, args.baud, logger, args.headless)
        if not connection.connect():
            connection = None

    # Global state for view mode
    view_mode = "ASCII" # or "HEX"

    def on_message(msg: str):
        if view_mode == "HEX":
            # Convert back to bytes using latin-1 (preserves 0-255)
            data_bytes = msg.encode('latin-1')
            hex_str = ' '.join(f"{b:02X}" for b in data_bytes)
            print(f"{Colors.CYAN}{hex_str}{Colors.ENDC}")
        else:
            print(f"{msg}")

    try:
        while True:
            try:
                if args.headless:
                    time.sleep(1)
                    continue

                user_input = input()
                
                if not user_input.strip():
                    continue

                if user_input.startswith('/'):
                    parts = user_input.split()
                    cmd = parts[0].lower()

                    if cmd == '/exit':
                        break
                    elif cmd == '/help':
                        print_help()
                        print(f"{Colors.BOLD}COMANDOS AVANZADOS:{Colors.ENDC}")
                        print(f"  {Colors.BOLD}/view [hex|ascii]{Colors.ENDC} : Cambiar modo de visualización.")
                        print(f"  {Colors.BOLD}/rts [on|off]{Colors.ENDC}     : Controlar línea RTS.")
                        print(f"  {Colors.BOLD}/dtr [on|off]{Colors.ENDC}     : Controlar línea DTR.")
                        print(f"  {Colors.BOLD}/status{Colors.ENDC}          : Ver estado de líneas modem.")
                    elif cmd == '/list':
                        list_available_ports()
                    elif cmd == '/clear':
                        os.system('cls' if os.name == 'nt' else 'clear')
                    elif cmd == '/disconnect':
                        if connection:
                            connection.disconnect()
                            connection = None
                        else:
                            print("No hay conexión activa.")
                    
                    elif cmd == '/view':
                        if len(parts) < 2:
                            print(f"Modo actual: {view_mode}")
                        else:
                            mode = parts[1].upper()
                            if mode in ["HEX", "ASCII"]:
                                view_mode = mode
                                print(f"Modo de visualización cambiado a {view_mode}")
                            else:
                                print("Modo inválido. Use HEX o ASCII.")

                    elif cmd == '/rts':
                        if isinstance(connection, SerialConnection):
                            state = True if len(parts) > 1 and parts[1].lower() == 'on' else False
                            connection.set_rts(state)
                        else:
                            print("Comando solo disponible en conexión serial.")

                    elif cmd == '/dtr':
                        if isinstance(connection, SerialConnection):
                            state = True if len(parts) > 1 and parts[1].lower() == 'on' else False
                            connection.set_dtr(state)
                        else:
                            print("Comando solo disponible en conexión serial.")

                    elif cmd == '/status':
                        if isinstance(connection, SerialConnection):
                            status = connection.get_modem_status()
                            print(f"{Colors.HEADER}Estado Modem:{Colors.ENDC}")
                            for k, v in status.items():
                                color = Colors.GREEN if v else Colors.FAIL
                                print(f"  {k}: {color}{v}{Colors.ENDC}")
                        else:
                            print("Comando solo disponible en conexión serial.")

                    elif cmd == '/connect':
                        # /connect serial COM3 115200 --rtscts
                        
                        if len(parts) < 2:
                            print("Uso: /connect [type] [args...]")
                            continue
                        
                        type_or_port = parts[1].lower()
                        
                        if connection:
                            connection.disconnect()
                            connection = None

                        if type_or_port == 'serial':
                            if len(parts) < 3:
                                print("Uso: /connect serial [port] [baud] [--rtscts] [--xonxoff]")
                                continue
                            port = parts[2]
                            baud = int(parts[3]) if len(parts) > 3 else 115200
                            
                            rtscts = '--rtscts' in parts
                            xonxoff = '--xonxoff' in parts
                            
                            connection = SerialConnection(port, baud, logger, args.headless, rtscts, xonxoff, on_message)
                            connection.connect()
                        
                        elif type_or_port == 'tcp':
                            if len(parts) < 4:
                                print("Uso: /connect tcp [host] [port]")
                                continue
                            host = parts[2]
                            port = int(parts[3])
                            connection = TCPClientConnection(host, port, logger, args.headless, on_message)
                            connection.connect()
                            
                        else:
                            # Legacy / default serial
                            port = parts[1]
                            baud = int(parts[2]) if len(parts) > 2 else 115200
                            connection = SerialConnection(port, baud, logger, args.headless, on_message=on_message)
                            connection.connect()

                    elif cmd == '/listen':
                        # /listen tcp 8080
                        if len(parts) < 3 or parts[1].lower() != 'tcp':
                            print("Uso: /listen tcp [port]")
                            continue
                        
                        if connection:
                            connection.disconnect()
                            connection = None
                            
                        port = int(parts[2])
                        connection = TCPServerConnection(port, logger, args.headless, on_message)
                        connection.connect()

                    elif cmd == '/udp':
                        # /udp local_port remote_host remote_port
                        if len(parts) < 4:
                            print("Uso: /udp [local_port] [remote_host] [remote_port]")
                            continue
                        
                        if connection:
                            connection.disconnect()
                            connection = None
                            
                        local_port = int(parts[1])
                        remote_host = parts[2]
                        remote_port = int(parts[3])
                        connection = UDPConnection(local_port, remote_host, remote_port, logger, args.headless, on_message)
                        connection.connect()

                    else:
                        print(f"Comando desconocido: {cmd}")
                else:
                    if connection and connection.is_connected:
                        data_to_send = user_input
                        
                        # Hex input parsing: #0A or $0A
                        if user_input.startswith(('#', '$')):
                            try:
                                # Remove prefix and spaces
                                hex_str = user_input[1:].replace(' ', '')
                                # Convert hex string to bytes, then decode to latin1/utf-8 to send as string?
                                # ConnectionHandler.send takes string.
                                # This is a limitation of current base class taking string.
                                # Ideally send should take bytes.
                                # For now, we decode bytes to string using latin1 to preserve byte values.
                                byte_data = bytes.fromhex(hex_str)
                                data_to_send = byte_data.decode('latin1')
                            except ValueError:
                                print(f"{Colors.FAIL}Error: Formato Hex inválido.{Colors.ENDC}")
                                continue

                        connection.send(data_to_send)
                    else:
                        print(f"{Colors.WARNING}No estás conectado. Usa /connect, /listen o /udp.{Colors.ENDC}")

            except KeyboardInterrupt:
                break
            except EOFError:
                break

    finally:
        if connection:
            connection.disconnect()
        if not args.headless:
            print("\nSaliendo...")

if __name__ == "__main__":
    main()
