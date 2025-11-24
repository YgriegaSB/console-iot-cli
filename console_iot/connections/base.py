from abc import ABC, abstractmethod
from ..utils.logger import Logger

class ConnectionHandler(ABC):
    def __init__(self, logger: Logger, headless: bool = False, on_message=None):
        self.logger = logger
        self.headless = headless
        self.on_message = on_message

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def send(self, data: str):
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        pass
