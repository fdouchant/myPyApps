import unittest

from os.path import dirname, join
from myPyApps import myconfig

class TestMyConfig(unittest.TestCase):

    def setUp(self):
        self.config = myconfig.MyConfigParser("myconfig")

    def test_override(self):
        self.assertEqual(self.config.get("section1", "opt_11"), "val_11_user")
        self.assertEqual(self.config.get("section1", "opt_12"), "val_12_default")
        self.assertEqual(self.config.get("section2", "opt_21"), "val_21_user")
    
    def test_reload(self):
        try:
            self.config.reload()
        except:
            self.fail("Should not raise any exception")
    
    def test_str(self):
        output = """[section1]
opt_11 = val_11_user
opt_12 = val_12_default
opt_13 = val_13_fail

[section2]
opt_21 = val_21_user
opt_22 = val_22_user

[section3_fail]
opt_3 = val_3

"""
        self.assertEqual(output, str(self.config))
    
    def test_check_override(self): 
        self.assertFalse(self.config.check_override_all())
        
        self.config.remove_section("section3_fail")
        self.assertFalse(self.config.check_override_all())
        
        self.config.remove_option("section1", "opt_13")
        self.assertTrue(self.config.check_override_all())
    
if __name__ == "__main__":
    unittest.main()    