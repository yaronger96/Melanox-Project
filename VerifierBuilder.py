from verifierComposite import verifierComposite
from WidthVerifier import WidthVerifier
from SpeedVerifier import SpeedVerifier
from CauseVerifier import CauseVerifier
from Monostate import Monostate

class VerifierBuilder:
    def __init__(self,speedValue,widthValue):
        # self.pciComponent = pciComponent
        self.verifierComposite = verifierComposite('verifier Composite')
        self.server = Monostate()
        self.speedValueToCompare = speedValue
        self.widthValueToCompare = widthValue
        

    def buildVerifier(self):

        self.buildCap()
        self.buildVerifierMlx()

    def buildCap(self):
        UscComponent = self.server.getUscComponent()
        DscComponent = self.server.getDscComponent()
        widthVerifierusc = WidthVerifier(UscComponent, self.widthValueToCompare)
        widthVerifierdsc = WidthVerifier(DscComponent, self.widthValueToCompare)
        speedVerifierusc = SpeedVerifier(UscComponent, self.speedValueToCompare)
        speedVerifierdsc = SpeedVerifier(DscComponent, self.speedValueToCompare)
        CapVerifierComposite = verifierComposite('cap verifier composite')
        CapVerifierComposite.addToverifierList(widthVerifierusc)
        CapVerifierComposite.addToverifierList(widthVerifierdsc)
        CapVerifierComposite.addToverifierList(speedVerifierusc)
        CapVerifierComposite.addToverifierList(speedVerifierdsc)
        self.verifierComposite.addToNodeList(CapVerifierComposite)

    def buildVerifierMlx(self):

        UscComponent=self.server.getUscComponent()
        DscComponent = self.server.getDscComponent()
        ######usc verifier comopsite
        uscVerifierComopsite = self.BuildCuaseVerifierComposite(UscComponent, "usc")
        if uscVerifierComopsite != -1:
            self.verifierComposite.addToNodeList(uscVerifierComopsite)
        dscVerifierComopsite = self.BuildCuaseVerifierComposite(DscComponent, "dsc")
        if dscVerifierComopsite != -1:
            self.verifierComposite.addToNodeList(dscVerifierComopsite)


    def BuildCuaseVerifierComposite(self, Component,uscOrDsc):
        DeviceName = Component.getDeviceName()
        if DeviceName is None : # not mlx device
           return -1  # no cause
        name = str(uscOrDsc) + " verifier composite"
        VerifierComposite = verifierComposite(name)
        if DeviceName is "shomron" or DeviceName is "dotan":
            pxd_causereg0Verifier = CauseVerifier(Component, "pxd_causereg0", 0xfe110000)
            VerifierComposite.addToverifierList(pxd_causereg0Verifier)
            npi_checks_causeregVerifier = CauseVerifier(Component, "npi_checks_causereg", 0xc000)
            VerifierComposite.addToverifierList(npi_checks_causeregVerifier)
            cause_fatal_causeregVerifier = CauseVerifier(Component, "cause_fatal_causereg", 0x0)
            VerifierComposite.addToverifierList(cause_fatal_causeregVerifier)
        elif DeviceName is "galil":
            pxd_causereg0Verifier = CauseVerifier(Component, "pxd_causereg0", 0xfe110000)
            VerifierComposite.addToverifierList(pxd_causereg0Verifier)
            npi_checks_causeregVerifier = CauseVerifier(Component, "npi_checks_causereg", 0x180f000)
            VerifierComposite.addToverifierList(npi_checks_causeregVerifier)
            cause_fatal_causeregVerifier = CauseVerifier(Component, "cause_fatal_causereg", 0x0)
            VerifierComposite.addToverifierList(cause_fatal_causeregVerifier)
        elif DeviceName is "BF":
            pxd_causereg0Verifier = CauseVerifier(Component, "pxd_causereg0",0xfe7d0808)
            VerifierComposite.addToverifierList(pxd_causereg0Verifier)
            npi_checks_causeregVerifier = CauseVerifier(Component, "npi_checks_causereg", 0x9c01f800)
            VerifierComposite.addToverifierList(npi_checks_causeregVerifier)
            cause_fatal_causeregVerifier = CauseVerifier(Component, "cause_fatal_causereg", 0x0)
            VerifierComposite.addToverifierList(cause_fatal_causeregVerifier)
        elif DeviceName is "negev":
            pxd_causereg0Verifier = CauseVerifier(Component, "pxd_causereg0", 0xfe7d0808)
            VerifierComposite.addToverifierList(pxd_causereg0Verifier)
            npi_checks_causeregVerifier = CauseVerifier(Component, "npi_checks_causereg", 0x7003f8e0)
            VerifierComposite.addToverifierList(npi_checks_causeregVerifier)
            cause_fatal_causeregVerifier = CauseVerifier(Component, "cause_fatal_causereg", 0x0)
            VerifierComposite.addToverifierList(cause_fatal_causeregVerifier)
        return VerifierComposite






