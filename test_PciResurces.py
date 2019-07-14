import unittest
from PciResurces import PciResurces
from crspace_agent import crspace_agent


class PciResurces(unittest.TestCase):
    def test_print(self):
        rec = PciResurces()
        rec.set_CRspace_agent(crspace_agent("This is cr space"))
        rec.print_feature()
