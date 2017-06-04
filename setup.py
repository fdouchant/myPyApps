from setuptools import setup, find_packages

try:
    from html2rest import html2rest
    from io import StringIO
    from urllib.request import urlopen
    
    # read content of article (plain html template) and convert to restructuredText for long_description
    stringIO = StringIO()
    html_content = urlopen("http://fabrice.douchant.com/mypyapps-framework-for-python-developments?lang=en").read()
    html2rest(html_content, writer=stringIO)
    long_description = stringIO.getvalue()
except (ImportError, IOError):
    print("Can't use spip article as description, use README.txt instead")
    long_description = open('README.txt').read()

import myPyApps

setup(
    name='myPyApps',
    version='.'.join(map(str, myPyApps.__version__)),
    packages=find_packages(),

    package_data={
        'myPyApps': ['config/*.default', 'logs/.empty'],
    },

    author='Fabrice Douchant',
    author_email='fabrice.douchant@gmail.com',
    description='Allow quick Python programs development',
    long_description=long_description,
    license='GNU GPLv3',
    keywords='framework tools',
    url="http://fabrice.douchant.com/mypyapps-framework-for-python-developments?lang=en"
)
