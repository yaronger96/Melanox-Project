from abc import abstractmethod
from EventHendler import EventHendler
from PciProperty import PciProperty

class verifier:
    def __init__(self, component , valueToCompare):
        self.valueToCompare = valueToCompare
        self.correntValue = 0
        self.componentForVerifier = component
        self.eventHendler = EventHendler()
        #self.iter = iter

    @abstractmethod
    def getValue(self):
        pass

    @abstractmethod
    def eval(self, iter):
        pass

    @abstractmethod
    def clean(self):
        pass






