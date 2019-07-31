from abc import abstractmethod
from EventHendler import EventHendler

class verifierComposite:
    def __init__(self, name):
        self.name = 'verifier'
        self.verifierList =list()
        self.nodeList = list()#[cap, usc, dsc]

       # self.valueToCompare = value_to_compare
       # self.correntValue = 0
       # self.componentForVerifier = component
       # self.eventHendler = EventHendler()
       # self.iter = iter

    def eval(self, iter, valueToCompare):
        if not self.nodeList: #list is empty
            for verifier in self.verifierList:
                verifier.eval(iter, valueToCompare)
        else:
            for node in self.nodeList:
                node.eval(iter, valueToCompare)

    def addToNodeList(self, verifierForNodeList):
        self.nodeList.append(verifierForNodeList)

    def addToverifierList(self, verifierForverifierList):
        self.verifierList.append(verifierForverifierList)

    # @abstractmethod
    # def getValue(self):
    #     pass
    #
    # @abstractmethod
    # def eval(self,):
    #     pass
    #
    # @abstractmethod
    # def clean(self):
    #     pass
    #
    # @abstractmethod
    # def clean(self):
    #     pass





