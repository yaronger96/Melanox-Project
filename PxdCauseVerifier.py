#data link layer verifier example
from verifier import verifier
import PxdCauseProperty

class PxdCauseVerifier(verifier):

    def getValue(self):
        RxErrorValue = PxdCauseProperty.PxdCauseProperty(self.componentForVerifier.resources).get_with_CRspace()
        self.correntValue = RxErrorValue


    def eval(self,):
        mask = 0xfd7fefff #1111 1101 0111 1111 1110 1111 1111 1111
        if self.correntValue & mask == self.valueToCompare:
            return
        error = 'Rx Error expected value: {} , but was: {}'.format(bin(self.valueToCompare), bin(self.correntValue))
        bdf = self.componentForVerifier.resources.conf_space_agent.getBdf()
        uscOrDsc = self.componentForVerifier.getUscOrDsc()
        self.eventHendler.addEvent(self.iter, error, bdf, uscOrDsc)