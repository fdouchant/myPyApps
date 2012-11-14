import unittest

import mypackage

from myPyApps import myapp

class TestMyApp(unittest.TestCase):
	
	def test_simple_implementation(self):
		class MyTest(myapp.MyApp):
			def main(self, text):
				return text			
		test = MyTest()
		self.assertEqual(test.run("Hello world !"), "Hello world !")
	
	def test_simple_implementation_module(self): 
		class MyPackageTest(myapp.MyApp):
			def main(self, text):
				return mypackage.return_string(text)
		test = MyPackageTest()
		self.assertEqual(test.run("Hello world !"), "Hello world !")

	def test_exception_implementation(self):
		class MyException(Exception): pass
		class MyFailingTest(myapp.MyApp):
			def main(self, text):
				raise MyException("an exception")
		test = MyFailingTest()
		self.assertRaises(MyException, test.run, "Hello world !")

if __name__ == "__main__":
	unittest.main()