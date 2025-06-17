from abc import ABC, abstractmethod


class AIEngine(ABC):
    @abstractmethod
    def get_response(self, message, persona_desc):
        pass

    @abstractmethod
    def test_connection(self):
        pass