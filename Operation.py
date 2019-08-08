from abc import abstractmethod


class Operation:
    
    def __init__(self):
        pass
    
    @abstractmethod
    def rescanPciBuses(self):    
        pass
    
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def checkGenOp(self):
        pass