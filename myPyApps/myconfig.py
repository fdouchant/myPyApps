"""
@author: Fabrice Douchant
@contact: vamp.higher@gmail.com
@license: GNU GPLv3 (LICENSE.txt)

myconfig is a module that provides easy to use configuration.
It is based on convention over configuration.
"""


from ConfigParser import SafeConfigParser
import os, sys, StringIO
from os.path import dirname, abspath, join, isfile

import logging
LOGGER = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(lineno)d:%(message)s", level=logging.DEBUG)


class MyConfigParserException(Exception):
    def __init__(self, name, message=None):
        Exception.__init__(self, message)
        self.name = name
    def __str__(self):
        return "[%s] %s" % (self.name, Exception.__str__(self))

# remove duplicate path
DEFAULT_PATH = [join(os.getenv('USERPROFILE') or os.getenv('HOME'), '.config'), join(abspath(dirname(sys.argv[0])), "config")]
DEFAULT_CFG_EXT = '.cfg'
DEFAULT_DEFAULT_EXT = '.default'

class MyConfigParser(SafeConfigParser, object):
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
        super(MyConfigParser, self).__init__()
        
        self.name = name
        self.cfg_filename = name + cfg_ext
        self.default_filename = name + default_ext
        self.config_path = config_path
        if not hasattr(self.config_path, "__iter__"):
            LOGGER.debug("convert single config_path to set")
            self.config_path = (config_path, )
        
        LOGGER.debug("remove duplicate configuration path")
        self.config_path = list(set(self.config_path))
        
        LOGGER.debug("find and load default cfg file")
        # in list order to respect path importance
        for path in self.config_path:
            full_path = join(path, self.default_filename)
            if isfile(full_path):
                self.default_path = full_path
                LOGGER.debug("default_path = " + self.default_path)
                break
        else:
            raise MyConfigParserException(self.name, "Couldn't find default config file")

        # call reload
        self.reload()
                
    def reload(self):
        """
        Reload configuration
        """
        LOGGER.debug("clean config")
        for section in self.sections():
            if not self.remove_section(section):
                raise MyConfigParserException(self.name, "Couldn't clean section %r" % section)
        
        # use readfp to raise Exception if error while loading
        self.readfp(open(self.default_path))

        LOGGER.debug("find and load user cfg files")
        # in reverse order to respect path importance order
        for path in reversed(self.config_path):
            full_path = join(path, self.cfg_filename)
            if isfile(full_path):
                LOGGER.info("Load file %r for %r" % (full_path, self.name))
                self.read(full_path)
        LOGGER.debug("done reload")
                
    def check_override_all(self):
        """
        Return true if user config override properly the default on (no extra variables).
        """
        default_cfg = SafeConfigParser()
        default_cfg.readfp(open(self.default_path))
        
        LOGGER.debug("test section differences")
        diff_sections = set(self.sections()) - set(default_cfg.sections())
        # should not have more section in user config
        if diff_sections:
            LOGGER.warn("%r sections are not in default" % diff_sections)
            return False
        LOGGER.debug("for each section, test option differences")
        for section in self.sections():
            diff_options = set(self.options(section)) - set(default_cfg.options(section))
            # should not have more options in user config
            if diff_options:
                LOGGER.warn("%r options are not in default section %r" % (diff_options, section))
                return False
        # all good
        return True

    def items(self, section, with_default=False):
        """
        Return a list of (name, value) pairs for each option in the given section.
        
        @section: the section to get options from.
        @param with_default: if with_default is True then items from default will be used in result (same behaviour than configParser)
        If false, default items will be skipped
        """
        all_items = super(MyConfigParser, self).items(section)
        if with_default:
            return all_items
        return list(set(all_items)-set(self.defaults().items()))

    def __str__(self):
        result = StringIO.StringIO()
        self.write(result)
        return result.getvalue()
