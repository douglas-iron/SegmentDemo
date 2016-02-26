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

configFile = os.environ.get('PAYLOAD_FILE')
print(configFile)

if configFile is None or configFile == "":
	configFile = opts.config

if configFile is None or configFile == "":
	print("Please specify the config json file with either '-config conf.json' or set the environment variable 'PAYLOAD_FILE=conf.json'")
	exit(1)

with open(configFile) as data_file:
	options = json.load(data_file)

oauthToken = None

if 'token' in options:
	oauthToken = options["token"]

projectid = None

if 'projectid' in options:
	projectid = options["projectid"]

mqServer = None

if 'mqServer' in options:
	mqServer = options["mqServer"]
else:
	print("Please specify \"mqServer\":\"mq-aws-us-east-1-1.iron.io\" or proper server name in Configuration file")

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

queueName = None
if 'queueName' in options:
        queueName = options["queueName"]
else:
	print("Please specify \"queueName\":\"QUEUENAME\"  in Configuration file")


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



otoken = "OAuth %s" % oauthToken
url = "https://%s/3/projects/%s/queues/%s/reservations" % (mqServer, projectid, queueName)

payload = "{\n  \"n\": 1,\n  \"timeout\": 60,\n  \"wait\": 0,\n  \"delete\": false\n}"
headers = {
    'authorization': otoken,
    'content-type': "application/json",
    'cache-control': "no-cache"
    }

response = requests.request("POST", url, data=payload, headers=headers)

test = response.text
data = json.loads(test)
if test is None or test == "":
    print("No messages in queue, exiting")
    exit(0)

reservationID = data["messages"][0]["reservation_id"]

print("Reservation ID: %s") % reservationID
pprint(data)

messageBody = data["messages"][0]["body"]
messageID = data["messages"][0]["id"]


bData = json.loads(messageBody)
userId = bData["userId"]
landType = bData["type"]

if landType == "page":
    title = bData["properties"]["title"]
    search = bData["properties"]["search"]
    print(search)
    if  ((search is None)) or (len(search) == 0):
        print("Not search object: %s" % search)
    else:
        m = re.search(r"=(.+)&.+=(.+)&.+=(.+)", search)
        print(m)
        userid = m.group(1)
        name = m.group(2)
        name = re.sub("\+", " ", name, 1)
        email = m.group(3)
        email = re.sub("\%40", "@", email, 1)

        print("Message ID: %s\n" % messageID)
        print("Landing Type: %s\n" % landType)
        print("Page Title: %s\n" % title)
        print("User ID: %s\n" % userid)
        print("Name: %s\n" % name)
        print("Email: %s\n" % email)
        message = "Hello %s,\nThank  you for visiting our page %s. Please come again!\nYour Friendly Sales Person\n" % (name, title) 

        send_mail("douglas@dactbc.com", email, title, message, files=None, data_attachments=None, server="smtp.office365.com", port=587,tls=True, html=False, images=None,
                                      username=sendEmail, password=emailPassword)

                                     

    delUrl = "https://%s/3/projects/%s/queues/%s/messages/%s" % (mqServer, projectid, queueName, messageID)

    payload = "{\n  \"reservation_id\": \"%s\"\n}" % reservationID
    delHeaders = {
	'authorization': otoken,
	'content-type': "application/json",
	'cache-control': "no-cache"
    }

    delResponse = requests.request("DELETE", delUrl, data=payload, headers=delHeaders)

    print(delResponse.text)
 
else:
    print("Message ID: %s\n" % messageID)
    print("Type: %s\n" % landType)
    print("Not the right type, ignoring\n")

    delUrl = "https://%s/3/projects/%s/queues/%s/messages/%s" % (mqServer, projectid, queueName, messageID)

    payload = "{\n  \"reservation_id\": \"%s\"\n}" % reservationID
    delHeaders = {
	'authorization': otoken,
	'content-type': "application/json",
	'cache-control': "no-cache"
    }

    delResponse = requests.request("DELETE", delUrl, data=payload, headers=delHeaders)
    print("Reservation ID: %s") % reservationID
    print("Message ID: %s") % messageID
    print(delResponse.text)
 



