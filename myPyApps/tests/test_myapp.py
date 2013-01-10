import unittest

import mypackage

from myPyApps import myapp, mylogging
import optparse

class TestMyApp(unittest.TestCase):
	
	def setUp(self):
		unittest.TestCase.setUp(self)
		class MyTest(myapp.MyApp):
			def main(self, text):
				return text
		self.test_class = MyTest	
		self.test_instance = MyTest()
	
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
		test = MyFailingTest(logging_email=False)
		self.assertRaises(MyException, test.run, "Hello world !")
		
	def test_send_email(self):
		class MyTest(myapp.MyApp):
			def main(self, text):
				logger = mylogging.getLogger(__name__)
				logger.send_email("my message", "my subject")
				return text		
		test = MyTest()
		self.assertEqual(test.run("Hello world !"), "Hello world !")
		
	def test_options_fail(self):
		try:
			self.assertRaises(Exception, self.test_class(options="won't work"))
		except: 
			pass
		else:
			self.fail("Test should have failed")
		
		
	def  test_options_not_myoptionparser(self):
		self.test_class(options=optparse.OptionParser().parse_args()[0])

			
if __name__ == "__main__":
	unittest.main()