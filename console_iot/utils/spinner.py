import sys
import time
import threading
from .colors import Colors

class Spinner:
    def __init__(self, message: str = "Cargando"):
        self.message = message
        self.running = False
        self.thread = None

    def _spin(self):
        dots = 0
        while self.running:
            sys.stdout.write(f'\r{Colors.CYAN}{self.message}{"." * dots}{" " * (5 - dots)}{Colors.ENDC}')
            sys.stdout.flush()
            
            dots = (dots + 1) % 6
            time.sleep(0.3)
    
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._spin, daemon=True)
            self.thread.start()
    
    def stop(self):
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=0.5)
            sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
            sys.stdout.flush()
