#pysical layer verifier example
from verifier import verifier
import RxErrorProperty

class RxErrorVerifier(verifier):

    def getValue(self):
        RxErrorValue = RxErrorProperty.RxErrorProperty(self.componentForVerifier.resources).get_with_CRspace()
        self.correntValue = RxErrorValue


    def eval(self,):
        mask = 0x3fffffB #0000 0011 1111 1111 1111 1111 1111 1011
        if self.correntValue & mask == self.valueToCompare:
            return
        error = 'Rx Error expected value: {} , but was: {}'.format(bin(self.valueToCompare), bin(self.correntValue))
        bdf = self.componentForVerifier.resources.conf_space_agent.getBdf()
        uscOrDsc = self.componentForVerifier.getUscOrDsc()
        self.eventHendler.addEvent(self.iter, error, bdf, uscOrDsc)