import unittest
from iatiflat import default_first
from iatiflat import replace_default_if_none
from iatiflat import recode_if_not_none
from iatiflat import make_versioned_code_dict

class RefactoredTestCase(unittest.TestCase):
    def test_default_first(self):
        self.assertTrue(default_first([]) is None)
    def test_replace_default_if_none(self):
        self.assertTrue(replace_default_if_none(None,1) == 1)
    def test_recode_if_not_none(self):
        self.assertTrue(recode_if_not_none(" ",{}) is None)
    def test_made_versioned_code_dict(self):
        self.assertTrue(make_versioned_code_dict("2.01")["Country"]["BD"]=="BANGLADESH")
        
if __name__ == '__main__':
    unittest.main()