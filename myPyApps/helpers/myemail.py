import smtplib, logging, string, os

import mimetypes

from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from myPyApps import mylogging

LOGGER = mylogging.getLogger(__name__)

def send_email(to_addrs, subject, text_body=None, html_body=None, attachements=[]):
    """
    This helper is used to send an email than may be in text or html and have attachments.
    It uses mylogging SMTPHandler default configuration (section handler_mail, option args)
    
    @param to_addrs: recievers addresses
    @param subject: the email subject
    @param text_body: an optional text body
    @param html_body: an optional html body
    @param attachements: an optional list of files to attach to the email 
    """
    
    # needs a list even if one email address
    if not hasattr(to_addrs, '__iter__'):
        LOGGER.debug("convert to_addrs has string")
        if "," in to_addrs:
            to_addrs = map(string.strip, to_addrs.split(','))
            LOGGER.debug("to_addrs is a string containing list of emails")
        else:
            to_addrs = [ to_addrs ]
    
    # unpack logging smtp handler configuration
    args = mylogging.DEFAULT_CONFIG.get('handler_mail', 'args', raw=True)
    LOGGER.debug("using smtp configuration: " + args)
    
    eval_args = eval(args, vars(logging))
    
    # unpack values, skip to_addrs and subject
    host, from_addr, _, _, = eval_args[:4]
    others = eval_args[4:]
    # get host and port
    if hasattr(others, '__iter__') and len(others) > 2:
        host = others[0]
        port = others[1]
    else:
        port = smtplib.SMTP_PORT
        LOGGER.debug("SMTP configuration uses default port " + str(port)) 
    
    # get credentials if any
    username = password = None
    if others:
        username, password = others[0]
        LOGGER.debug("found username = %s, password = %s" % (username, password))
    # get secure if any  
    secure = None
    if len(others) > 1:
        secure = others[1]
        LOGGER.debug("found secure = " + str(secure))
        
        
    # create message container - the correct MIME type is multipart/alternative.
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['To'] = ", ".join(to_addrs)
    message['From'] = from_addr
    
    # Record the MIME types of both parts - text/plain and text/html.
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    if text_body:
        LOGGER.debug("add text body")
        part1 = MIMEText(text_body, 'plain')
        message.attach(part1)
    if html_body:
        LOGGER.debug("add html body")
        part2 = MIMEText(html_body, 'html')
        message.attach(part2)
        
        
    # add any attachements
    for attachement in attachements:
        LOGGER.debug("add attachement from file " + str(attachement))
        add_attachment(message, attachement, os.path.basename(attachement))
    
    
    smtp = smtplib.SMTP(host, port)
    if username:
        LOGGER.debug("initial credentials for SMTP")
        if secure is not None:
            LOGGER.debug("start TLS")
            smtp.ehlo()
            smtp.starttls(*secure)
            smtp.ehlo()
        smtp.login(username, password)
    smtp.sendmail(from_addr, to_addrs, message.as_string())
    smtp.quit()
    
    
    
def add_attachment(message, filename, name=None):
    """
    Add an attachment to 'message'.
    Try to find its type in order to properly set its header.
    
    @param message: the given message to add the file to
    @param filename: the attachement file path
    @param name: an optional name for the attachment
    """
    
    ctype, encoding = mimetypes.guess_type(filename)
    
    if ctype is None or encoding is not None:
        # No guess could be made, or the file is encoded (compressed), so
        # use a generic bag-of-bits type.
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        fp = open(filename)
        # Note: we should handle calculating the charset
        attachement = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == 'image':
        fp = open(filename, 'rb')
        attachement = MIMEImage(fp.read(), _subtype=subtype)
        fp.close()
    elif maintype == 'audio':
        fp = open(filename, 'rb')
        attachement = MIMEAudio(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(filename, 'rb')
        attachement = MIMEBase(maintype, subtype)
        attachement.set_payload(fp.read())
        fp.close()
        # Encode the payload using Base64
        encoders.encode_base64(attachement)
    # Set the filename parameter
    attachement.add_header('Content-Disposition', 'attachment', filename=name or filename)
    message.attach(attachement)
