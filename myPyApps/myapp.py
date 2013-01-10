"""
@author: Fabrice Douchant
@contact: vamp.higher@gmail.com
@license: GNU GPLv3 (LICENSE.txt)

myapp is class to inherit to take benefits of this framework tools that are easy to use and convention oriented.

You should use in your main script like this:

from myPyApps import myapp

class MyProgram(myapp.MyApp):
    def main(self, <myargs>):
        # my code here
        
if __name__ == "__main__":
    return MyProgram.run(<myargs>)
"""


import os, glob, sys
from os.path import basename, splitext
import optparse

from myPyApps import myconfig, mylogging, myoptionparser

LOGGER = mylogging.getLogger(__name__)

class MyApp():
    """
    Parent class to construct my application from.
    
    Inherit from this class, then override the 'main()' function with any arguments you want.
    Then run the application by calling the 'run()' function with the appropriate main arguments.
    """
    
    def __init__(self, config_default=splitext(basename(sys.argv[0]))[0], 
                 config_path=myconfig.DEFAULT_PATH, 
                 config_filter=[],
                 logging_email=True, 
                 options={}):
        """
        This initialize the application by getting all configuration files
        
        @param config_default: name of the config that will be used as default. Default = name of the script (without any extension) 
        The default config will be directly available as a configParse object in the class as self.CONFIG and its default section will be available as a dictionary in self.DEFAULTS
        @param config_path: the configuration path. 
        @param config_filter: the configuration filter. Found configuration that are listed in config_filter will be ignored.
        @param logging_email: to turn on or off email logging
        @param options: options that will be used to configure the framework. Can be either:
            - a dictionary (empty for default values).
            - an optparse.Values instance. Tippicaly  using myoptionparser (e.g myoptionparser.MyOptionParser.parse_args())
            Handled keys/options are: 'dry_run' (default: False), 'verbose' (default: False) and 'config' (default: []). If a key/option is missing, program will take the default
        """
        
        self.options = options
        # init logging. To send emails, dry_run must be false AND logging_email param must be true 
        mylogging.configure_logging(not self.get_option('dry_run', False) and logging_email, self.get_option('verbose', False))
        
        # use options to initialize config_path
        self.config_path = self.get_option('config', [])
        # add all other config_path
        self.config_path.extend(config_path)
        LOGGER.debug("initialize application with config_path %r and config_filter %r" % (self.config_path, config_filter))
        self.CONFIGS = {}
        self.CONFIG = None
        self.DEFAULTS = None

        LOGGER.debug("get all configuration names that have a default file")        
        names = []
        for path in self.config_path:
            for f in glob.glob(os.path.join(path, '*' + myconfig.DEFAULT_DEFAULT_EXT)):
                conf = os.path.splitext(os.path.basename(f))[0]
                if conf in config_filter:
                    LOGGER.info("Skip config %r" % conf)
                    continue
                if conf in names:
                    LOGGER.warn("Duplicate default configuration for %r from %r" % (conf, f))
                    continue
                LOGGER.debug("found configuration %r from %r" % (conf, f))
                names.append(conf)
        
        LOGGER.debug("load configurations")        
        for name in names:
            self.CONFIGS[name] = myconfig.MyConfigParser(name, config_path=self.config_path)
            if name == config_default:
                LOGGER.debug("%r is the default configuration" % conf)
                self.CONFIG = self.CONFIGS[name]
                self.DEFAULTS = self.CONFIG.defaults()
                
        LOGGER.debug("Add logging in configs")
        self.CONFIGS['logging'] = mylogging.DEFAULT_CONFIG
        
        if not self.CONFIGS:
            LOGGER.warn("No configuration loaded")
        if not self.CONFIG:
            LOGGER.warn("No default configuration loaded")
            self.DEFAULTS = {}
    
    def get_option(self, key, default=None):
        """
        Get the option value for the given key.
        
        @param key: the key to look for
        @param default: the default value if key is not found
        
        Returns the value for key or default if not found (default is None by default) 
        """
        if hasattr(self.options, 'get'):
            return self.options.get(key, default)
        elif hasattr(self.options, 'ensure_value'):
            return self.options.ensure_value(key, default)
        else:
            raise Exception("options type %s doesn't support any getter method" % self.options.__class__)
    
    def main(self):
        """
        The function to override
        """
        raise NotImplementedError()
    
    def run(self, *args, **kwargs):
        """
        The function run the main() function with its arguments and log unhandled exceptions
        """
        try:
            return self.main(*args, **kwargs)
        except Exception as e:
            LOGGER.exception("Exception raised: " + str(e))
            raise e