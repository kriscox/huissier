import unittest

from vcs import VcsList


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here

    def test_isin(self):
        VCSList = VcsList()
        self.assertTrue('000125776765' in VCSList, "VCS 000125776765 not found in list, but in list")
        self.assertTrue('000125776766' not in VCSList, "VCS 000125776766 found in list, but not in list")

    def test_add(self):
        VCSList = VcsList()
        VCSList += '000125776767'
        self.assertTrue('000125776767' in VCSList, "VCS not added to list")


if __name__ == '__main__':
    unittest.main()
