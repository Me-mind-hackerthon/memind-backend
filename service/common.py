from abc import ABC, abstractmethod

class ObjectCreator(ABC):
    def __init__(self, session) -> None:
        self.session = session

    @abstractmethod
    async def create_object(self, object_info):
        pass