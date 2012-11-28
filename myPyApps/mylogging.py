"""
@author: Fabrice Douchant
@contact: vamp.higher@gmail.com
@license: GNU GPLv3 (LICENSE.txt)

mylogging is a module that provides standard logging configuration.
It will log into console (stdout, stderr), file (rotating), smtp for exception.

You should use it once in your program like this:

from myPyApps import mylogging
mylogging.configure_logging()
"""

import logging, logging.handlers, logging.config, StringIO

from os.path import join, dirname


from myPyApps import myconfig

# add new classes to logging

class MaxLevelFilter(logging.Filter):
    """
    Allow to define a max_level. This will emit logs only in range [level, maxlevel]
    """
    def __init__(self, name='', max_level=None):
        super(MaxLevelFilter, self).__init__(name)
        self.max_level = max_level
        
    def filter(self, rec):
        if self.max_level:
            return rec.levelno <= self.max_level
        else:
            return True


class StreamMaxLevelHandler(logging.StreamHandler):
    """
    Emit logs only in range [level, maxlevel]
    """
    def __init__(self, stream=None, max_level=None):
        super(StreamMaxLevelHandler, self).__init__(stream)
        self.addFilter(MaxLevelFilter('maxlevelfilter', max_level))
        

class MySMTPHandler(logging.handlers.SMTPHandler):
    """
    Like a SMTPHandler except if connect to SMTP fails, it will only alert once and
    will log into a lower level (not just displaying the error like in SMTPHandler)
    """
    def __init__(self, *args, **kwargs):
        super(MySMTPHandler, self).__init__(*args, **kwargs)
        self.first_error = True
    
    def handleError(self, *args, **kwargs):
        # don't spam in logs
        if self.first_error:
            # just try to use lowest level
            super(MySMTPHandler, self).handleError(*args, **kwargs)
            try:
                import sys, traceback
                print >> sys.stderr, ("Error with SMTP handler. Please check your configuration file. "
                                  "Or disable email 'mylogging.configure_logging(mail=False)'.\n"), traceback.format_exc()
            except:
                pass
        self.first_error = False
        
    def emit_email(self, record, subject=None):
        """
        Send an email with record text and subject
        """
        # thread safe
        self.acquire()
        
        # backup handler's instance variables
        bkp_subject = self.subject
        bkp_formatter = self.formatter
        # change instance variables
        self.subject = subject
        self.formatter = logging.Formatter("%(message)s")
        try:
            self.emit(record)
        finally:
            self.subject = bkp_subject
            self.formatter = bkp_formatter
            self.release()
     
        
class MyLogger(logging.Logger):
    
    def send_email(self, msg, subject=None):
        """
        Send an email to all SMTP handlers. Precisely to all handlers having emit_email method.    
        """
        record = logging.LogRecord(self.name, logging.INFO, None, None, msg, None, None)
        for h in logging.root.handlers:
            if hasattr(h, 'emit_email'):
                h.emit_email(record, subject)

# override some logging variables
logging.setLoggerClass(MyLogger)
logging.Logger.manager = logging.Manager(logging.root)

def getLogger(name=None):
    """
    Mimic default logging.getLogger implementation but uses MyLogger as class
    
    @param name: the name of the logger. If none, will be 'root'
    """
    return logging.getLogger(name)
        

def configure_logging(mail=True, config=myconfig.MyConfigParser('logging', config_path=myconfig.DEFAULT_PATH+[join(dirname(__file__), "config")])):
    """
    Method to use to init logging, then you may use logging usually.
    
    @param mail: set to False to disable email logging
    @param config: to give another way to find logging configuration. 
    Default is to take logging.default and user defined logging.cfg in HOME, script, module dir
    """
    result = StringIO.StringIO()
    config.write(result)
    # rewind io
    result.seek(0)
    try:
        logging.config.fileConfig(result, disable_existing_loggers=False)
    except Exception as e:
        # already default format
        logging.exception("Error configuring mylogging: " + str(e))
        return
    
    for h in filter(lambda h: isinstance(h, logging.handlers.RotatingFileHandler), logging.root.handlers):
        try:
            h.doRollover()
        except WindowsError:
            logging.error("Could not rollover " + str(h))
            pass
    
    # disable mail
    if not mail:
        logging.info("Disable SMTP")
        logging.root.handlers = filter(lambda h: not isinstance(h, logging.handlers.SMTPHandler), logging.root.handlers)
