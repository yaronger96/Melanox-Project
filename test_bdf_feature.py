import unittest
from bdf_feature import bdf_feature


class TestBdfFeature(unittest.TestCase):

    def test_eq(self):
        usc_bdf = bdf_feature(bdf="86:00.0")
        dsc_bdf = bdf_feature(bdf="86:00.0")
        self.assertEqual(usc_bdf == dsc_bdf, True)


if __name__ == '__main__':
    unittest.main()


