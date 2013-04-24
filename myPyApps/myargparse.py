"""
@author: Fabrice Douchant
@contact: vamp.higher@gmail.com
@license: GNU GPLv3 (LICENSE.txt)

myargparse is wrapper package over argparse that sets some defaults options (quiet, verbose, config).

Example:

from myPyApps import myargparse

parser = myargparse.MyArgumentParser()
namespace = parser.parse_args()
"""


from argparse import ArgumentParser
from myPyApps import mylogging
import os

LOGGER = mylogging.getLogger(__name__)

QUIET = "quiet"
VERBOSE = "verbose"
CONFIG = "config"
DUMP_CONFIG = "dump-config"


class MyArgumentParser(ArgumentParser):
    
    def parse_args(self, args=None, namespace=None):
        """
        Initialize and parse args with default options then validate those default options.
        The default options: 
            - quiet: disable logging emails
            - verbose: set stdout to debug
            - config: set a new path to the config path (with highest priority)
        
        Return (options, args) or exit if there is an issue
        """
        
        # initialize
        self.add_argument("-q", "--quiet", action="store_true", dest=QUIET, default=False, 
                        help="run in dry mode. In case of use as myapp init parser parameter, it disables logging emails")
        self.add_argument("-v", "--verbose", action="store_true", dest=VERBOSE, default=False, 
                        help="run in verbose mode. In case of use as myapp init parser parameter, it sets stdout to debug")
        self.add_argument("-c", "--config", action="append", dest=CONFIG, default=[], 
                        help="run in dry mode. In case of use as myapp init parser parameter, it sets a new path to the config path (with highest priority)")
        self.add_argument("--dump-config", action="store_true", dest=DUMP_CONFIG, default=False,
                        help="display all configurations and exit")
        
        # parse
        args = ArgumentParser.parse_args(self, args=None, namespace=None)
        
        # validate
        for config in args.config:
            if not os.path.isdir(config):
                self.error("config options must be valid folders. %r is not" % config)
                
        return args