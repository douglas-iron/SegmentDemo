import sys
sys.path.append("packages")
import json
from pprint import pprint
import requests
import os
import re
import smtplib
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
	print("Starting without config file\n\n")
else:
    with open(configFile) as data_file:
        options = json.load(data_file)

hostName = "https://endpoint1.collection.us2.sumologic.com"
sumoUrl = "/receiver/v1/http/ZaVnC4dhaV26LHNZoUn1KT-OF-zkmYimLeQ9QGbGNUF_9p9nSnJe7cudJahPFWxnMdQcZc0CBKlrGhfuNMXOAQqnplGYqvhb_OKcSuQSEFPfsbXwPI106Q=="
segResultFile = "seg_result.txt"

def createResultFile(file,content):
    resultFile = open(file, 'a')
    data = content
    resultFile.write(data.encode('utf8'))
    resultFile.write("\n")
    resultFile.close


def sendData(file):
    # var http = require("https");

    # var options = {
    #   "method": "POST",
    #   "hostname": hostName,
    #   "port": null,
    #   "path": sumoUrl,
    #   "headers": {
    #     "cache-control": "no-cache"
    #   }
    # };

    # var req = http.request(options, function (res) {
    #   var chunks = [];

    #   res.on("data", function (chunk) {
    #     chunks.push(chunk);
    #   });

    #   res.on("end", function () {
    #     var body = Buffer.concat(chunks);
    #     console.log(body.toString());
    #   });
    # });

    # req.end();
    httpEndpoint = "%s/%s" % (hostName, sumoUrl)
    r = requests.post(httpEndpoint, files={file: open(file, 'rb')})

bData = None
with open(payload) as data_file:
	bData  = json.load(data_file)

print("Source:\n")
print(bData)

if bData is None or bData == "":
	print("Payload file empty or not given")
	exit(2)
userId = bData["userId"]
landType = bData["type"]

if landType == "page" or landType == "identify" or landType == "track":
    title = bData["context"]["page"]["title"]
    referrer = bData["context"]["page"]["referrer"]
    path = bData["context"]["page"]["path"]
    url = bData["context"]["page"]["url"]
    userid = bData["userId"]
    if "firstName" in bData["context"]["traits"]:
        firstName = bData["context"]["traits"]["firstName"]
    else:
        firstName = "N/A"

    if "lastName" in bData["context"]["traits"]:
        lastName = bData["context"]["traits"]["lastName"]
    else:
        lastName = "N/A"

    if "email" in bData["context"]["traits"]:
        email = bData["context"]["traits"]["email"]
    else:
        email = "N/A"

    if "username" in bData["context"]["traits"]:
        username = bData["context"]["traits"]["username"]
    else:
        username = "N/A"
    package = bData["context"]["library"]["name"]
    packageVer = bData["context"]["library"]["version"]

    userAgent = bData["context"]["userAgent"]
    library = "%s-%s" % (package,packageVer)

    if "ip" in bData["context"]:
        ip = bData["context"]["ip"]
    else:
        ip = "0.0.0.0"

    segmentMsgID = bData["messageId"]

    timestamp = bData["originalTimestamp"]
    name = "%s %s" % (firstName, lastName)

    if landType == "identify":
        anonId = bData["anonymousId"]
    else:
        anonId = "N/A"

    if landType == "track":
        event = bData["event"]
    else: 
        event = "N/A"


    print("\n\nParsed Data:\n\n")
    print("Landing Type: %s" % landType.encode('utf8'))
    print("Page Title: %s" % title.encode('utf8'))
    if landType == "identify":
        print("Anonymous ID: %s" % anonId.encode('utf8'))
    if landType == "track":
        print("Event: %s" % event.encode('utf8'))
    print("User ID: %s" % userid.encode('utf8'))
    print("Username: %s" % username.encode('utf8')) 
    print("Name: %s" % name.encode('utf8'))
    print("Email: %s" % email.encode('utf8'))
    print("Context:")
    print("\tURL: %s" % url.encode('utf8'))
    print("\tPath: %s" % path.encode('utf8'))
    print("\tReferrer: %s" % referrer.encode('utf8'))
    print("Timetamp: %s" % timestamp.encode('utf8'))
    print("Client Data")
    print("\tUserAgent: %s" % userAgent.encode('utf8'))
    print("\tLibrary: %s" % library.encode('utf8'))
    print("\tIP: %s" % ip.encode('utf8'))
    print("SegmentMsgID: %s" % segmentMsgID.encode('utf8'))

    if landType == "identify":
        anonId = bData["anonymousId"]
        message = "{\"type\":\"%s\",\"timestamp\":\"%s\",\"segmentMsgID\":\"%s\",\"anonId\":\"%s\",\"userid\":\"%s\",\"title\":\"%s\",\"username\":\"%s\",\"name\":\"%s\",\"email\":\"%s\",\"url\":\"%s\",\"path\":\"%s\",\"referrer\":\"%s\",\"userAgent\":\"%s\",\"library\":\"%s\",\"ip\":\"%s\"}" % (landType, timestamp, segmentMsgID, anonId, userid, title, username, name, email, url, path, referrer, userAgent,library,ip)

    if landType == "track":
        message = "{\"type\":\"%s\",\"timestamp\":\"%s\",\"segmentMsgID\":\"%s\",\"event\":\"%s\",\"userid\":\"%s\",\"title\":\"%s\",\"username\":\"%s\",\"name\":\"%s\",\"email\":\"%s\",\"url\":\"%s\",\"path\":\"%s\",\"referrer\":\"%s\",\"userAgent\":\"%s\",\"library\":\"%s\",\"ip\":\"%s\"}" % (landType, timestamp, segmentMsgID, event, userid, title, username, name, email, url, path, referrer, userAgent,library,ip)

    if landType == "page":
        message = "{\"type\":\"%s\",\"timestamp\":\"%s\",\"segmentMsgID\":\"%s\",\"userid\":\"%s\",\"title\":\"%s\",\"username\":\"%s\",\"name\":\"%s\",\"email\":\"%s\",\"url\":\"%s\",\"path\":\"%s\",\"referrer\":\"%s\",\"userAgent\":\"%s\",\"library\":\"%s\",\"ip\":\"%s\"}" % (landType, timestamp, segmentMsgID, userid, title, username, name, email, url, path, referrer, userAgent,library,ip)


    createResultFile(segResultFile, message)
    sendData(segResultFile)


else:
    print("Type: %s\n" % landType)
    print("Unknown type, ignoring\n")
