import serial
import threading
import queue
import time
from typing import Optional
from .base import ConnectionHandler
from ..utils.logger import Logger
from ..utils.colors import Colors

class SerialConnection(ConnectionHandler):
    def __init__(self, port: str, baudrate: int, logger: Logger, headless: bool = False, 
                 rtscts: bool = False, xonxoff: bool = False, on_message=None):
        super().__init__(logger, headless, on_message)
        self.port = port
        self.baudrate = baudrate
        self.rtscts = rtscts
        self.xonxoff = xonxoff
        self.serial_conn: Optional[serial.Serial] = None
        self._is_connected = False
        self.stop_event = threading.Event()
        self.read_thread: Optional[threading.Thread] = None
        self.rx_queue = queue.Queue()

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def connect(self) -> bool:
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1,
                rtscts=self.rtscts,
                xonxoff=self.xonxoff
            )
            self._is_connected = True
            self.stop_event.clear()
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            msg = f"Conectado a {self.port} a {self.baudrate} baudios (RTS/CTS={self.rtscts}, XON/XOFF={self.xonxoff})."
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

    def set_rts(self, level: bool):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.rts = level
            self.logger.log(f"RTS set to {level}", "SYS")

    def set_dtr(self, level: bool):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.dtr = level
            self.logger.log(f"DTR set to {level}", "SYS")

    def get_modem_status(self):
        if self.serial_conn and self.serial_conn.is_open:
            return {
                "CTS": self.serial_conn.cts,
                "DSR": self.serial_conn.dsr,
                "RI": self.serial_conn.ri,
                "CD": self.serial_conn.cd
            }
        return {}

    def disconnect(self):
        if self._is_connected:
            self.stop_event.set()
            if self.read_thread:
                self.read_thread.join(timeout=1.0)
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
            self._is_connected = False
            msg = "Desconectado."
            self.logger.log(msg, "SYS")
            if not self.headless:
                print(f"{Colors.WARNING}{msg}{Colors.ENDC}")

    def send(self, data: str):
        if not self._is_connected or not self.serial_conn:
            print(f"{Colors.FAIL}No hay conexión establecida.{Colors.ENDC}")
            return

        try:
            # Agregar terminador por defecto \n si no se especifica otro
            if not data.endswith(('\n', '\r')):
                data += '\n'
            
            self.serial_conn.write(data.encode('utf-8'))
            self.logger.log(data.strip(), "TX")
        except Exception as e:
            msg = f"Error enviando datos: {e}"
            self.logger.log(msg, "ERROR")
            if not self.headless:
                print(f"{Colors.FAIL}{msg}{Colors.ENDC}")

    def _read_loop(self):
        while not self.stop_event.is_set() and self.serial_conn and self.serial_conn.is_open:
            try:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('latin-1').strip()
                    if line:
                        self.logger.log(line, "RX")
                        if not self.headless and self.on_message:
                            self.on_message(line)
                        elif not self.headless:
                            print(f"{line}")
            except Exception as e:
                self.logger.log(f"Error de lectura: {e}", "ERROR")
                break
def list_available_ports():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No se encontraron puertos COM.")
    else:
        print(f"{Colors.HEADER}Puertos disponibles:{Colors.ENDC}")
        for p in ports:
            print(f"  - {p.device}: {p.description}")
