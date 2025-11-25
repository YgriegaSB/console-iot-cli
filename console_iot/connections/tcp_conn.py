import socket
import threading
import time
from typing import Optional
from .base import ConnectionHandler
from ..utils.logger import Logger
from ..utils.colors import Colors

class TCPClientConnection(ConnectionHandler):
    def __init__(self, host: str, port: int, logger: Logger, headless: bool = False, on_message=None):
        super().__init__(logger, headless, on_message)
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self._is_connected = False
        self.stop_event = threading.Event()
        self.read_thread: Optional[threading.Thread] = None

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None) # Blocking mode for reading
            
            self._is_connected = True
            self.stop_event.clear()
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            msg = f"Conectado a TCP {self.host}:{self.port}"
            self.logger.log(msg, "SYS")
            if not self.headless:
                print(f"{Colors.GREEN}{msg}{Colors.ENDC}")
            return True
        except Exception as e:
            msg = f"Error conectando a TCP {self.host}:{self.port}: {e}"
            self.logger.log(msg, "ERROR")
            if not self.headless:
                print(f"{Colors.FAIL}{msg}{Colors.ENDC}")
            return False

    def disconnect(self):
        if self._is_connected:
            self.stop_event.set()
            if self.socket:
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                    self.socket.close()
                except:
                    pass
            if self.read_thread:
                self.read_thread.join(timeout=1.0)
            
            self._is_connected = False
            msg = "Desconectado TCP."
            self.logger.log(msg, "SYS")
            if not self.headless:
                print(f"{Colors.WARNING}{msg}{Colors.ENDC}")

    def send(self, data: str):
        if not self._is_connected or not self.socket:
            print(f"{Colors.FAIL}No hay conexión establecida.{Colors.ENDC}")
            return

        try:
            if not data.endswith(('\n', '\r')):
                data += '\n'
            
            self.socket.sendall(data.encode('utf-8'))
            self.logger.log(data.strip(), "TX")
        except Exception as e:
            msg = f"Error enviando datos TCP: {e}"
            self.logger.log(msg, "ERROR")
            if not self.headless:
                print(f"{Colors.FAIL}{msg}{Colors.ENDC}")
            self.disconnect()

    def _read_loop(self):
        while not self.stop_event.is_set() and self._is_connected:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break # Connection closed
                
                line = data.decode('latin-1').strip()
                if line:
                    self.logger.log(line, "RX")
                    if not self.headless and self.on_message:
                        self.on_message(line)
                    elif not self.headless:
                        print(f"{line}")
            except Exception as e:
                if not self.stop_event.is_set():
                    self.logger.log(f"Error de lectura TCP: {e}", "ERROR")
                break
        
        if not self.stop_event.is_set():
            self.disconnect()
            if not self.headless:
                print(f"{Colors.FAIL}Conexión cerrada por el servidor.{Colors.ENDC}")


class TCPServerConnection(ConnectionHandler):
    def __init__(self, port: int, logger: Logger, headless: bool = False, on_message=None):
        super().__init__(logger, headless, on_message)
        self.port = port
        self.server_socket: Optional[socket.socket] = None
        self.client_socket: Optional[socket.socket] = None
        self.client_addr = None
        self._is_connected = False
        
        self.stop_event = threading.Event()
        self.accept_thread: Optional[threading.Thread] = None
        self.read_thread: Optional[threading.Thread] = None

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def connect(self) -> bool:
        # Starts the server
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(1)
            
            self._is_connected = True
            self.stop_event.clear()
            self.accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
            self.accept_thread.start()
            
            msg = f"Servidor TCP escuchando en puerto {self.port}"
            self.logger.log(msg, "SYS")
            if not self.headless:
                print(f"{Colors.GREEN}{msg}{Colors.ENDC}")
            return True
        except Exception as e:
            msg = f"Error iniciando servidor TCP en {self.port}: {e}"
            self.logger.log(msg, "ERROR")
            if not self.headless:
                print(f"{Colors.FAIL}{msg}{Colors.ENDC}")
            return False

    def disconnect(self):
        self.stop_event.set()
        
        # Close client if any
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
            except:
                pass
        
        # Close server
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        if self.accept_thread:
            pass

        self._is_connected = False
        msg = "Servidor TCP detenido."
        self.logger.log(msg, "SYS")
        if not self.headless:
            print(f"{Colors.WARNING}{msg}{Colors.ENDC}")

    def send(self, data: str):
        if not self.client_socket:
            print(f"{Colors.FAIL}No hay cliente conectado.{Colors.ENDC}")
            return

        try:
            if not data.endswith(('\n', '\r')):
                data += '\n'
            
            self.client_socket.sendall(data.encode('utf-8'))
            self.logger.log(data.strip(), "TX")
        except Exception as e:
            msg = f"Error enviando datos a cliente TCP: {e}"
            self.logger.log(msg, "ERROR")
            if not self.headless:
                print(f"{Colors.FAIL}{msg}{Colors.ENDC}")
            # Close client
            self.client_socket = None

    def _accept_loop(self):
        while not self.stop_event.is_set():
            try:
                client, addr = self.server_socket.accept()
                self.client_socket = client
                self.client_addr = addr
                
                msg = f"Cliente conectado desde {addr}"
                self.logger.log(msg, "SYS")
                if not self.headless:
                    print(f"{Colors.GREEN}{msg}{Colors.ENDC}")
                
                # Start reading from client
                self._read_client_loop()
                
            except Exception as e:
                if not self.stop_event.is_set():
                    pass
                break

    def _read_client_loop(self):
        while not self.stop_event.is_set() and self.client_socket:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                
                line = data.decode('latin-1').strip()
                if line:
                    self.logger.log(line, "RX")
                    if not self.headless and self.on_message:
                        self.on_message(line)
                    elif not self.headless:
                        print(f"{line}")
            except Exception as e:
                break
        
        if self.client_socket:
            self.client_socket.close()
        self.client_socket = None
        msg = "Cliente desconectado."
        self.logger.log(msg, "SYS")
        if not self.headless:
            print(f"{Colors.WARNING}{msg}{Colors.ENDC}")
