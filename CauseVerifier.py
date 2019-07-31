from CauseBulkProperty import CauseBulkProperty
from verifier import verifier


class CauseVerifier(verifier):
    def __init__(self, component, nameOfCause, mask, valueToCompare=0):
        verifier.__init__(self, component, valueToCompare)
        self.nameOfCause = nameOfCause
        self.mask = mask


    def getValue(self):
        BulkValue = CauseBulkProperty(self.componentForVerifier.resources, self.nameOfCause).get_with_CRspace()
        self.correntValue = BulkValue



    def eval(self,iter):
        self.getValue()
        # mask = 0x3fffffB #0000 0011 1111 1111 1111 1111 1111 1011
        if self.correntValue & self.mask == self.valueToCompare:
            return
        error = '{} expected value: {} , but was: {}'.format(self.nameOfCause, bin(self.valueToCompare), bin(self.correntValue))
        bdf = self.componentForVerifier.resources.conf_space_agent.getBdf()
        uscOrDsc = self.componentForVerifier.getUscOrDsc()
        self.eventHendler.addEvent(iter, error, bdf, uscOrDsc)