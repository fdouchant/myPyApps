from myPyApps import mylogging

LOGGER = mylogging.getLogger(__name__) 

def return_string(text):
    LOGGER.info("mypackage.return_string")
    return text