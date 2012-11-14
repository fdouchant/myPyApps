from distutils.core import setup

import myPyApps

setup(
    name='myPyApps',
    version='.'.join(map(str, myPyApps.__version__)),
    author='Fabrice Douchant',
    author_email='vamp.higher@gmail.com',   
    description='Allow quick Python programs development',
    long_description=open('README.txt').read(),
    license='GNU GPLv3',
    platforms = ["any"],
    keywords='framework tools',
    url='http://fabricedouchant.com/spip.php?article52&lang=en',
    packages=['myPyApps'],
    package_data={
       'myPyApps': ['config/*.default'],
    },
)