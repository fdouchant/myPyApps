def test_all():
    import unittest
    from os.path import dirname
    loader = unittest.TestLoader()
    suite = loader.discover(dirname(__file__))
    unittest.TextTestRunner().run(suite)
    
if __name__ == "__main__":
    test_all()