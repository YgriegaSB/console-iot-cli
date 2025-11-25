import socket
import threading
from typing import Optional
from .base import ConnectionHandler
from ..utils.logger import Logger
from ..utils.colors import Colors

class UDPConnection(ConnectionHandler):
    def __init__(self, local_port: int, remote_host: str, remote_port: int, logger: Logger, headless: bool = False, on_message=None):
        super().__init__(logger, headless, on_message)
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.socket: Optional[socket.socket] = None
        self._is_connected = False
        self.stop_event = threading.Event()
        self.read_thread: Optional[threading.Thread] = None

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def connect(self) -> bool:
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(('0.0.0.0', self.local_port))
            
            self._is_connected = True
            self.stop_event.clear()
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            msg = f"UDP escuchando en {self.local_port}, enviando a {self.remote_host}:{self.remote_port}"
            self.logger.log(msg, "SYS")
            if not self.headless:
                print(f"{Colors.GREEN}{msg}{Colors.ENDC}")
            return True
        except Exception as e:
            msg = f"Error iniciando UDP en {self.local_port}: {e}"
            self.logger.log(msg, "ERROR")
            if not self.headless:
                print(f"{Colors.FAIL}{msg}{Colors.ENDC}")
            return False

    def disconnect(self):
        if self._is_connected:
            self.stop_event.set()
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
            if self.read_thread:
                self.read_thread.join(timeout=1.0)
            
            self._is_connected = False
            msg = "UDP detenido."
            self.logger.log(msg, "SYS")
            if not self.headless:
                print(f"{Colors.WARNING}{msg}{Colors.ENDC}")

    def send(self, data: str):
        if not self._is_connected or not self.socket:
            print(f"{Colors.FAIL}No hay socket UDP activo.{Colors.ENDC}")
            return

        try:
            if not data.endswith(('\n', '\r')):
                data += '\n'
            
            self.socket.sendto(data.encode('utf-8'), (self.remote_host, self.remote_port))
            self.logger.log(data.strip(), "TX")
        except Exception as e:
            msg = f"Error enviando datos UDP: {e}"
            self.logger.log(msg, "ERROR")
            if not self.headless:
                print(f"{Colors.FAIL}{msg}{Colors.ENDC}")

    def _read_loop(self):
        while not self.stop_event.is_set() and self._is_connected:
            try:
                data, addr = self.socket.recvfrom(1024)
                if not data:
                    continue
                
                line = data.decode('latin-1').strip()
                if line:
                    log_msg = f"[{addr[0]}:{addr[1]}] {line}"
                    self.logger.log(log_msg, "RX")
                    if not self.headless and self.on_message:
                        self.on_message(line)
                    elif not self.headless:
                        print(f"{line}")
            except Exception as e:
                if not self.stop_event.is_set():
                    pass
                break
