from distutils.core import setup

try:
    from html2rest import html2rest
    from StringIO import StringIO
    import urllib
    
    # read content of article (plain html template) and convert to restructuredText for long_description
    stringIO = StringIO()
    html_content = urllib.urlopen("http://fabricedouchant.com/spip.php?page=article_plain_html&id_article=52&lang=en").read()
    html2rest(html_content, writer=stringIO)
    long_desc = stringIO.getvalue()
except (ImportError, IOError):
    print "Can't use spip article as description, use README.txt instead"
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
    url="http://fabricedouchant.com/spip.php?article52&lang=en",
    packages=['myPyApps', 'myPyApps.helpers'],
    package_data={
       'myPyApps': ['config/*.default'],
    },
)