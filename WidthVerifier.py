from verifier import verifier
from WidthProperty import WidthProperty

class WidthVerifier(verifier):

    def getValue(self):
        widthValue = WidthProperty(self.componentForVerifier.resources).get()
        self.correntValue = widthValue

    def eval(self, iter):
        self.getValue()
        if self.correntValue == self.valueToCompare:
            return
        error = 'width expected value: {} , but was: {}'.format(self.valueToCompare, self.correntValue)
        bdf = self.componentForVerifier.resources.conf_space_agent.getBdf()
        uscOrDsc = self.componentForVerifier.getUscOrDsc()
        self.eventHendler.addEvent(iter, error, bdf, uscOrDsc)

    def clean(self):
        pass
