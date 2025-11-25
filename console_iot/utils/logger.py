import os
import datetime
from .colors import Colors

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
