import sys
sys.path.append("packages")
import json
from pprint import pprint
import requests
import os
import re
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import ConfigParser
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-config')
opts = parser.parse_args()

payload = os.environ.get('PAYLOAD_FILE')
print(payload)

configFile = ""
configFile = opts.config

if configFile is None or configFile == "":
	print("Please specify the config json file with either '-config conf.json'")
	exit(1)

with open(configFile) as data_file:
	options = json.load(data_file)

sendEmail = None
if 'sendEmail' in options:
        sendEmail = options["sendEmail"]
else:
	print("Please specify \"sendEmail\":\"EMAIL\"  in Configuration file")

emailPassword = None
if 'emailPassword' in options:
        emailPassword = options["emailPassword"]
else:
	print("Please specify \"emailPassword\":\"PASSWORD\"  in Configuration file")


def send_mail(send_from, send_to, subject, text, files=None, 
                          data_attachments=None, server="smtp.office365.com", port=587, 
                          tls=True, html=False, images=None,
                          username=None, password=None, 
                          config_file=None, config=None):

    if files is None:
        files = []

    if images is None:
        images = []

    if data_attachments is None:
        data_attachments = []

    if config_file is not None:
        config = ConfigParser.ConfigParser()
        config.read(config_file)

    if config is not None:
        server = config.get('smtp', 'server')
        port = config.get('smtp', 'port')
        tls = config.get('smtp', 'tls').lower() in ('true', 'yes', 'y')
        username = config.get('smtp', 'username')
        password = config.get('smtp', 'password')

    msg = MIMEMultipart('related')
    msg['From'] = send_from
    msg['To'] = send_to if isinstance(send_to, basestring) else COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text, 'html' if html else 'plain') )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    for f in data_attachments:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( f['data'] )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % f['filename'])
        msg.attach(part)

    for (n, i) in enumerate(images):
        fp = open(i, 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()
        msgImage.add_header('Content-ID', '<image{0}>'.format(str(n+1)))
        msg.attach(msgImage)

    smtp = smtplib.SMTP(server, int(port))
    if tls:
        smtp.starttls()

    if username is not None:
        smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

bData = None
with open(payload) as data_file:
	bData  = json.load(data_file)
print(bData)

if bData is None or bData == "":
	print("Payload file empty or not given")
	exit(2)
userId = bData["userId"]
landType = bData["type"]

if landType == "page":
    title = bData["properties"]["title"]
    search = bData["properties"]["search"]
    print(search)
    if  ((search is None)) or (len(search) == 0):
        print("Not search object: Search=%s Title=%s" % (search,title))
    else:
        m = re.search(r"=(.+)&.+=(.+)&.+=(.+)", search)
        print(m)
        userid = m.group(1)
        name = m.group(2)
        name = re.sub("\+", " ", name, 1)
        email = m.group(3)
        email = re.sub("\%40", "@", email, 1)

        print("Landing Type: %s\n" % landType)
        print("Page Title: %s\n" % title)
        print("User ID: %s\n" % userid)
        print("Name: %s\n" % name)
        print("Email: %s\n" % email)
        message = "Hello %s,\nThank  you for visiting our page %s. Please come again!\nYour Friendly Sales Person\n" % (name, title) 

        send_mail("douglas@dactbc.com", email, title, message, files=None, data_attachments=None, server="smtp.office365.com", port=587,tls=True, html=False, images=None,
                                      username=sendEmail, password=emailPassword)

                                     


 
else:
    print("Type: %s\n" % landType)
    print("Not the right type, ignoring\n")
