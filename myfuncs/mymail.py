import sys,smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os
import ConfigParser
cur= os.path.dirname(__file__)
if cur=='': cur = '.'
CONFIG_FILE = '%s/config.txt'%cur

def mail(to = 'yuruliny@gmail.com',
	 subject = 'python script',
	 text = "This is a email sent with python",
	 attach = None,
	 config_file=CONFIG_FILE):
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    gmail_user = config.get('Gmail', 'username')
    gmail_pwd = config.get('Gmail', 'password')
    msg = MIMEMultipart()

    msg['From'] = gmail_user
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    part = MIMEBase('application', 'octet-stream')
    Encoders.encode_base64(part)
    if os.path.exists(attach):
	part.set_payload(open(attach, 'rb').read())
	part.add_header('Content-Disposition',
	       'attachment; filename="%s"' % os.path.basename(attach))
	msg.attach(part)

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()


def main(argv):
    args = set( a.lower() for a in sys.argv[1:] )
    for i,arg in enumerate(argv):
	if arg in ['-h','--help']:
	    print 'usage:'
	    print 'python mymail to_user@domain.com <subject> <text> <attachment>'
	if arg in ['-t','--test']:
	    mail("yuruliny@gmail.com",
	       "Hello from python!",
	       "This is a email sent with python",
	       "my_picture.jpg")
	    
if __name__ == '__main__': 
    main(sys.argv[1:])
