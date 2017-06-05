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
from os.path import basename, splitext, join, dirname

from myPyApps import myconfig, mylogging, myargparse

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
            - a Namespace instance. Tipicaly  using myargumentparser (e.g myargumentparser.MyArgumentParser.parse_args())
            Handled keys/options are: 'quiet' (default: False), 'verbose' (default: False) and 'config' (default: []). If a key/option is missing, default will be used
        """
        
        self.config_default = config_default
        self.options = options
        
        # use options to initialize config_path
        self.config_path = self.get_option(myargparse.CONFIG, [])
        # add all other config_path
        self.config_path.extend(config_path)
        module_path = join(dirname(__import__(self.__module__).__file__), 'config')
        LOGGER.debug("add module configuration folder %r" % module_path)
        self.config_path.append(module_path)
        LOGGER.debug("remove duplicate configuration path")
        self.config_path = list(set(self.config_path))
        
        # init logging. To send emails, quiet must be false AND logging_email param must be true 
        LOGGER.info("Logging configuration")
        mylogging.configure_logging(mail=not self.get_option(myargparse.QUIET, False) and logging_email, verbose=self.get_option(myargparse.VERBOSE, False), config_path=self.config_path)
        
        LOGGER.info("Application configuration")
        LOGGER.debug("initialize application with config_default %r, config_path %r and config_filter %r" % (self.config_default, self.config_path, config_filter))
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
                
        if not self.CONFIGS:
            LOGGER.warn("No configuration loaded")
        if not self.CONFIG:
            LOGGER.warn("No default configuration loaded")
            self.DEFAULTS = {}
            
        if self.get_option(myargparse.DUMP_CONFIG):
            for key, config in self.CONFIGS.iteritems():
                stars = "*" * 10
                print("%s %s %s\n" % (stars, key, stars))
                print(config, "")
            sys.exit(1)
    
    def get_option(self, key, default=None):
        """
        Get the option value for the given key.
        
        @param key: the key to look for
        @param default: the default value if key is not found. If set to None and the option it will throw an AttributeError exception
        @raise AttributeError: if the key is not found and default is None
        
        Returns the value for key or default if not found (default is None by default) 
        """
        try:
            if hasattr(self.options, '__getattribute__'):
                return self.options.__getattribute__(key)
        except AttributeError:
            pass
        try:
            if hasattr(self.options, '__getitem__'):
                return self.options.__getitem__(key)
        except KeyError:
            LOGGER.warn('Could not find option %r, use default %r' % (key, default))
            return default
        # if couldn't find anything
        raise Exception("options type %s doesn't support any getter method" % self.options.__class__)

    def main(self):
        """
        The function to override
        """
        raise NotImplementedError()

    def init(self):
        """
        The function to initialize things before the self.main() method is called
        """
        pass
    
    def run(self, *args, **kwargs):
        """
        The function run the main() function with its arguments and log unhandled exceptions
        """
        try:
            self.init()
            return self.main(*args, **kwargs)
        except Exception as e:
            LOGGER.exception("Exception raised: " + str(e))
            raise e