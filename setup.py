from distutils.core import setup

spip_url = "http://fabricedouchant.com/spip.php?article52&lang=en"
try:
    from html2rest import html2rest
    from StringIO import StringIO
    
    # read content of article (plain html template) and convert to restructuredText for long_description
    stringIO = StringIO()
    html2rest(open(spip_url+'&page=article_plain_html').read(), writer=stringIO, preprocess=lambda html, encoding: html.replace('<code', '<pre').replace('</code>', '</pre>'))
    long_desc = stringIO.getvalue()
except ImportError:
    print "Couldn't load html2rest, use README.txt as description"
    long_desc = open('README.txt').read()

import myPyApps

setup(
    name='myPyApps',
    version='.'.join(map(str, myPyApps.__version__)),
    author='Fabrice Douchant',
    author_email='vamp.higher@gmail.com',   
    description='Allow quick Python programs development',
    long_description=long_desc,
    license='GNU GPLv3',
    platforms = ["any"],
    keywords='framework tools',
    url=spip_url,
    packages=['myPyApps'],
    package_data={
       'myPyApps': ['config/*.default'],
    },
)