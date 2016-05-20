"""
*******************************************************************************
*   Ledger Blue
*   (c) 2016 Ledger
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      http://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License.
********************************************************************************
"""

import sys
import argparse
import os
import struct
import urllib2, urlparse
from BlueHSMServer_pb2 import Request, Response, Parameter
from ledgerblue.comm import getDongle


def serverQuery(request, url):
	data = request.SerializeToString()
	url = urlparse.urlparse(args.url)
	req = urllib2.Request(args.url, data, {"Content-type": "application/octet-stream" })
	res = urllib2.urlopen(req)
	data = res.read()
	response = Response()
	response.ParseFromString(data)
	if len(response.exception) <> 0:
		raise Exception(response.exception)
	return response


parser = argparse.ArgumentParser()
parser.add_argument("--url", help="Server URL")
parser.add_argument("--apdu", help="Display APDU log", action='store_true')
parser.add_argument("--perso", help="Personalization key reference to use")
parser.add_argument("--persoNew", help="New personalziation key reference to use")

args = parser.parse_args()
if args.url == None:
	raise Exception("No URL specified")
if args.perso == None:
	raise Exception("No personalization specified")
if args.persoNew == None:
	raise Exception("No new personalization specified")

dongle = getDongle(args.apdu)

# Identify

targetid = bytearray(struct.pack('>I', 0x31800001))
apdu = bytearray([0xe0, 0x04, 0x00, 0x00]) + bytearray([len(targetid)]) + targetid
dongle.exchange(apdu)

# Initialize chain 

dongle.exchange(bytearray.fromhex('E050000000'))

# Get remote certificate

request = Request()
request.reference = "refactory"
parameter = request.remote_parameters.add()
parameter.local = False
parameter.alias = "persoKey"
parameter.name = args.perso

response = serverQuery(request, args.url)

offset = 0

remotePublicKey = response.response[offset : offset + 65]
offset += 65
remotePublicKeySignatureLength = ord(response.response[offset + 1]) + 2
remotePublicKeySignature = response.response[offset : offset + remotePublicKeySignatureLength]

certificate = bytearray([len(remotePublicKey)]) + remotePublicKey + bytearray([len(remotePublicKeySignature)]) + remotePublicKeySignature
apdu = bytearray([0xE0, 0x51, 0x00, 0x00]) + bytearray([len(certificate)]) + certificate
dongle.exchange(apdu)

# Walk the chain

while True:
		certificate = bytearray(dongle.exchange(bytearray.fromhex('E052000000')))
		if len(certificate) == 0:
			break
		request = Request()
		request.reference = "refactory"
		request.id = response.id
		request.parameters = str(certificate)
		serverQuery(request, args.url)

# Commit agreement and send script

request = Request()
request.reference = "refactory"
parameter = request.remote_parameters.add()
parameter.local = False
parameter.alias = "persoKeyNew"
parameter.name = args.persoNew
request.id = response.id

response = serverQuery(request, args.url)
responseData = bytearray(response.response)

dongle.exchange(bytearray.fromhex('E053000000'))

offset = 0 
while offset < len(responseData):
	apdu = responseData[offset : offset + 5 + responseData[offset + 4]]
	dongle.exchange(apdu)
	offset += 5 + responseData[offset + 4]

