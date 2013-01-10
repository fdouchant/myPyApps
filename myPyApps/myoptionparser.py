"""
@author: Fabrice Douchant
@contact: vamp.higher@gmail.com
@license: GNU GPLv3 (LICENSE.txt)

myoptionparser is wrapper class over optparse.OptionParser that sets some defaults options (dry_run, verbose, config).

Example:

from myPyApps import myoptionparser

parser = myoptionparser.MyOptionParser()
(options, args) = parser.parse_args()
"""


from optparse import OptionParser
from myPyApps import mylogging
import os

LOGGER = mylogging.getLogger(__name__)

class MyOptionParser(OptionParser):
    
    def parse_args(self, args=None, values=None):
        """
        Initialize and parse args with default options then validate those default options.
        The default options: 
            - dry_run: disable logging emails
            - verbose: set stdout to debug
            - config: set a new path to the config path (with highest priority)
        
        Return (options, args) or exit if there is an issue
        """
        
        # initialize
        self.add_option("--dry_run", action="store_true", dest="dry_run", default=False, 
                        help="run in dry mode. In case of use as myapp init parser parameter, it disables logging emails")
        self.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, 
                        help="run in verbose mode. In case of use as myapp init parser parameter, it sets stdout to debug")
        self.add_option("-c", "--config", action="append", dest="config", default=[], 
                        help="run in dry mode. In case of use as myapp init parser parameter, it sets a new path to the config path (with highest priority)")
        
        # parse
        (options, args) = OptionParser.parse_args(self, args, values)
        
        # validate
        for config in options.ensure_value('config', []):
            if not os.path.isdir(config):
                self.error("config options must be valid folders. %r is not" % config)
                
        return (options, args)