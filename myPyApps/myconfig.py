"""
@author: Fabrice Douchant
@contact: vamp.higher@gmail.com
@license: GNU GPLv3 (LICENSE.txt)

myconfig is a module that provides easy to use configuration.
It is based on convention over configuration.
"""


from configparser import ConfigParser
import os, sys, io
from os.path import dirname, abspath, join, isfile

# will be used before mylogging initialization
import logging
LOGGER = logging.getLogger(__name__)
# check if python is in debug mode (python -d) for logging level
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)d:%(message)s", level=sys.flags.debug and logging.DEBUG or logging.INFO)


class MyConfigParserException(Exception):
    def __init__(self, name, message=None):
        Exception.__init__(self, message)
        self.name = name
    def __str__(self):
        return "[%s] %s" % (self.name, Exception.__str__(self))

# remove duplicate path
DEFAULT_PATH = [join(os.getenv('USERPROFILE') or os.getenv('HOME'), '.config'), join(abspath(dirname(sys.argv[0])), "config"), join(dirname(__file__), "config")]
DEFAULT_CFG_EXT = '.cfg'
DEFAULT_DEFAULT_EXT = '.default'

class MyConfigParser(ConfigParser, object):
    """
    Main class to build your configuration. It is an extension of SafeConfigParser. 
    """
    
    def __init__(self, name, config_path=DEFAULT_PATH, cfg_ext=DEFAULT_CFG_EXT, default_ext=DEFAULT_DEFAULT_EXT):
        """
        Create new MyConfigParser that extends ConfigParser.SafeConfigParser
        
        @param name: name of the config to look for and load
        @param config_path: path where to find the config files. Sort by order of importance.
        This will be used to first load default configuration and fail in there isn't any.
        Then it will load all user configurations in the respecting order of the list. Overriding default and previous user configuration.   
        @param cfg_ext: extension for the user configuration file.
        @param default_ext: extension for the default configuration file.
        
        @raise MyConfigParserException: if no default configuration found. 
        """
        ConfigParser.__init__(self)
        
        self.name = name
        self.cfg_filename = name + cfg_ext
        self.default_filename = name + default_ext
        self.config_path = config_path
        if not hasattr(self.config_path, "__iter__"):
            LOGGER.debug("[%s] convert single config_path to set" % self.name)
            self.config_path = (config_path, )
        
        LOGGER.debug("[%s] remove duplicate configuration path" % self.name)
        self.config_path = list(set(self.config_path))
        
        LOGGER.debug("[%s] find and load default cfg file" % self.name)
        # in list order to respect path importance
        for path in self.config_path:
            full_path = join(path, self.default_filename)
            if isfile(full_path):
                self.default_path = full_path
                LOGGER.debug("[%s] default_path = %s" % (self.name, self.default_path))
                break
        else:
            raise MyConfigParserException(self.name, "Couldn't find default config file")

        # call reload
        self.reload()
                
    def reload(self):
        """
        Reload configuration
        """
        LOGGER.debug("[%s] clean config" % self.name)
        for section in self.sections():
            if not self.remove_section(section):
                raise MyConfigParserException(self.name, "Couldn't clean section %r" % section)
        
        # use readfp to raise Exception if error while loading
        LOGGER.info("[%s] Load DEFAULT file %r" % (self.name, self.default_path))
        self.readfp(open(self.default_path))

        LOGGER.debug("[%s] find and load user cfg files" % self.name)
        # in reverse order to respect path importance order
        for path in reversed(self.config_path):
            full_path = join(path, self.cfg_filename)
            if isfile(full_path):
                LOGGER.info("[%s] Load config file %r" % (self.name, full_path))
                self.read(full_path)
        LOGGER.debug("[%s] done reload" % self.name)
                
    def check_override_all(self):
        """
        Return true if user config override properly the default on (no extra variables).
        """
        default_cfg = ConfigParser()
        default_cfg.read_file(open(self.default_path))
        
        LOGGER.debug("[%s] test section differences" % self.name)
        diff_sections = set(self.sections()) - set(default_cfg.sections())
        # should not have more section in user config
        if diff_sections:
            LOGGER.warn("[%s] %r sections are not in default" % (self.name, diff_sections))
            return False
        LOGGER.debug("[%s] for each section, test option differences" % self.nam)
        for section in self.sections():
            diff_options = set(self.options(section)) - set(default_cfg.options(section))
            # should not have more options in user config
            if diff_options:
                LOGGER.warn("[%s] %r options are not in default section %r" % (self.name, diff_options, section))
                return False
        # all good
        return True

    def items(self, section, with_default=False):
        """
        Return a list of (name, value) pairs for each option in the given section.
        
        @section: the section to get options from.
        @param with_default: if with_default is True then items from default will be used in result (same behavior than configParser)
        If false, default items will be skipped
        """
        all_items = ConfigParser.items(self, section)
        if with_default:
            return all_items
        return list(set(all_items)-set(self.defaults().items()))

    def __str__(self):
        result = io.StringIO()
        self.write(result)
        return result.getvalue()
