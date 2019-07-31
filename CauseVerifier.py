
from verifier import verifier
import RxErrorProperty

class CauseVerifier(verifier):
    def __init__(self, component, nameOfCause, mask, valueToCompare=0):
        verifier.__init__(self, component, valueToCompare)
        self.nameOfCause = nameOfCause
        self.mask = mask



    def getValue(self):
        BulkValue = CauseBulkProperty(self.componentForVerifier.resources, self.nameOfCause).get_with_CRspace()
        self.correntValue =BulkValue


    def eval(self,iter):
        self.getValue()
        sizeinbits = CauseBulkProperty(self.componentForVerifier.resources, self.nameOfCause).getsize()
        mask_for_check = 0b0
        # mask = 0x3fffffB #0000 0011 1111 1111 1111 1111 1111 1011
        status_after_mask = self.correntValue & ~self.mask
        if status_after_mask == self.valueToCompare:
            return
        error = 'Cause name:{}, these bits were 1:\n'.format(self.nameOfCause)
        for bit in range(sizeinbits):
            if status_after_mask & mask_for_check != 0:
                error = error + "{},".format(bit)
            mask_for_check = mask_for_check << 1

        bdf = self.componentForVerifier.resources.conf_space_agent.getBdf()
        uscOrDsc = self.componentForVerifier.getUscOrDsc()
        self.eventHendler.addEvent(iter, error, bdf, uscOrDsc)