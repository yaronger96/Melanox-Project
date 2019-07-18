from abc import abstractmethod
from EventHendler import EventHendler

class verifier:
    def __init__(self, value_to_compare, component,iter):
        self.valueToCompare = value_to_compare
        self.correntValue = value_to_compare
        self.componentForVerifier = component
        self.eventHendler = EventHendler()
        self.iter = iter

    @abstractmethod
    def getValue(self):
        pass

    @abstractmethod
    def eval(self,):
        pass

    @abstractmethod
    def clean(self):
        pass

    @abstractmethod
    def clean(self):
        pass





