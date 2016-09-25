# -*- coding: utf-8 -*-
#
#  auth.py                                          # # # # # # # # # #
#                                                                      #
#  Copyright 2016 Giorgio Ladu <giorgio.ladu >at< gmail.com>           #
#                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");      #
# you may not use this file except in compliance with the License.     #
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# # # # # # #
# 08.09.2016 V. 1.08
##

import pyrad.packet
import cgi

import cgitb #debug
cgitb.enable()

import socket
import sys
import time
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import store
import html_page
import config

form = cgi.FieldStorage()
stage = form.getfirst("stage", "login")  # counters or login,logout
mac = form.getvalue("mac", "00:00:00:00")
ip = form.getfirst("ip", "0.0.0.0")

incoming = form.getvalue("incoming", 0)
outgoing = form.getvalue("outgoing", 0)

gw_address = form.getvalue("gw_address", config.node_ip)
gw_port = form.getvalue("gw_port", config.node_port)
gw_id = form.getvalue("gw_id", config.node_name)
url = form.getvalue("url", config.custom_url)

token = form.getfirst("token")

ACCOUNT_STATUS_ERROR = -1
ACCOUNT_STATUS_DENIED = 0
ACCOUNT_STATUS_ALLOWED = 1
ACCOUNT_STATUS_VALIDATION = 5
ACCOUNT_STATUS_VALIDATION_FAILED = 6
ACCOUNT_STATUS_LOCKED = 254

radius_config = {
    'server': config.radius_server,  # radius server
    'secret': config.radius_secret,  # radius secret key
    'dict': Dictionary(config.radius_dictionary),
}


def SendPacket(srv, req):
    try:
        return srv.SendPacket(req)
    except pyrad.client.Timeout:
        html_page.error_page("RADIUS server does not reply")
        sys.exit(1)
    except socket.error as error:
        html_page.error_page("Network error: " + str(error[1]))
        sys.exit(1)

srv = Client(**radius_config)
auth_response = ACCOUNT_STATUS_DENIED
auth_message = "User Access FAILL", ACCOUNT_STATUS_VALIDATION_FAILED

if (token):
    if stage == "login":
        store_data = store.store_key(token)
        if store_data["username"]:
            store_data["session_start"] = time.time()
            req = srv.CreateAuthPacket(
                code=pyrad.packet.AccessRequest,
                User_Name=store_data["username"])
            req["Acct-Status-Type"] = "Start"
            req["User-Password"] = req.PwCrypt(store_data["password"])

            req["NAS-IP-Address"] = gw_address
            req["NAS-Port"] = config.custom_nas_port
            req["NAS-Port-Type"] = config.custom_nas_port_type
            # MAC OF WIFIDOG "00-10-A4-23-19-C0"
            req["NAS-Identifier"] = config.node_mac
            req["Acct-Session-Id"] = token
            # MAC OF WIFIDOG "00-10-A4-23-19-C0"
            req["Called-Station-Id"] = config.node_mac
            # MAC OF USER OR IP "00-00-B4-23-19-C0"
            req["Calling-Station-Id"] = mac
            req["Framed-IP-Address"] = ip
            req["Service-Type"] = pyrad.packet.AccessRequest
            req["Acct-Delay-Time"] = 0
            req["Acct-Input-Octets"] = 0
            req["Acct-Output-Octets"] = 0
            # WISPr-Location-ID =
            # "isocc=,cc=,ac=,network=Coova,Wicoin_Test"
            req["WISPr-Location-ID"] = str(config.custom_wispr_location_id)
            # WISPr-Location-Name = "Wicoin_Test"
            req["WISPr-Location-Name"] = str(
                config.custom_wispr_location_name)

            reply = SendPacket(srv, req)
            if reply.code == pyrad.packet.AccessAccept:
                auth_response = ACCOUNT_STATUS_ALLOWED
                auth_message = " User is now log in ", reply.code
                store_data["auth"] = True
                for i in reply.keys():
                    store_data[i] = reply[i][0]
            elif reply.code == pyrad.packet.AccessReject:
                auth_message = " User Access Reject ", reply.code
                auth_response = ACCOUNT_STATUS_VALIDATION_FAILED
                store_data["auth"] = False
            else:
                auth_message = " An error occurred during the validation process ", reply.code
                auth_response = ACCOUNT_STATUS_ERROR
                store_data["auth"] = False
            store_data.save()

    if stage == "counters":  # COUNTERS
        store_data = store.store_key(token)
        maxoctets = abs(int(outgoing) + int(incoming))

        req = srv.CreateAcctPacket(User_Name=store_data["username"])
        req["Acct-Status-Type"] = "Interim-Update"
        req["Acct-Session-Id"] = token
        req["Acct-Input-Octets"] = int(incoming)
        req["Acct-Output-Octets"] = int(outgoing)
        req["Acct-Delay-Time"] = 0

        req["NAS-IP-Address"] = gw_address
        req["NAS-Port"] = config.custom_nas_port
        req["NAS-Port-Type"] = config.custom_nas_port_type
        # MAC OF WIFIDOG "00-10-A4-23-19-C0"
        req["NAS-Identifier"] = config.node_mac

        # MAC OF WIFIDOG"00-10-A4-23-19-C0"
        req["Called-Station-Id"] = config.node_mac
        # MAC OF USER OR IP "00-00-B4-23-19-C0"
        req["Calling-Station-Id"] = mac
        req["Framed-IP-Address"] = ip

        SessionTime = int(time.time() - store_data["session_start"])
        req["Acct-Session-Time"] = abs(SessionTime)

        reply = SendPacket(srv, req)

        if "ChilliSpot-Max-Total-Octets" in store_data:
            if (maxoctets >= store_data["ChilliSpot-Max-Total-Octets"]):
                store_data["auth"] = False
                auth_response = ACCOUNT_STATUS_DENIED
        if "Session-Timeout" in store_data:
            if (0 >= int(store_data["Session-Timeout"])):
                store_data["auth"] = False
                auth_response = ACCOUNT_STATUS_DENIED
        elif reply.code == pyrad.packet.AccountingResponse:
            store_data["auth"] = True
            auth_response = ACCOUNT_STATUS_ALLOWED
        else:
            store_data["auth"] = False
            auth_response = ACCOUNT_STATUS_DENIED

        auth_message = "Sending Alive packet", reply.code
        store_data.save()

    if stage == "logout":  # STOP
        store_data = store.store_key(token)
        req = srv.CreateAcctPacket(User_Name=store_data["username"])
        req["NAS-IP-Address"] = gw_address
        req["NAS-Port"] = config.custom_nas_port
        req["NAS-Port-Type"] = config.custom_nas_port_type
        # MAC OF WIFIDOG "00-10-A4-23-19-C0"
        req["NAS-Identifier"] = config.node_mac

        req["Acct-Delay-Time"] = 0
        req["Acct-Status-Type"] = "Stop"
        req["Acct-Terminate-Cause"] = "Session Timeout"
        SessionTime = int(time.time() - store_data["session_start"])
        req["Acct-Session-Time"] = abs(SessionTime)
        req["Acct-Session-Id"] = token
        # MAC OF WIFIDOG"00-10-A4-23-19-C0"
        req["Called-Station-Id"] = config.node_mac
        # MAC OF USER OR IP "00-00-B4-23-19-C0"
        req["Calling-Station-Id"] = mac
        req["Framed-IP-Address"] = ip

        req["Acct-Input-Octets"] = int(incoming)
        req["Acct-Output-Octets"] = int(outgoing)

        reply = srv.SendPacket(req)
        auth_response = ACCOUNT_STATUS_DENIED
        auth_message = " User is now logged out ", reply.code
        print "Attributes returned by server:"
        for i in reply.keys():
            print "%s: %s" % (i, reply[i])
        store_data["auth"] = False
        store_data.delete()

print 'Auth:', auth_response
print 'Messages:', auth_message[0], " code:", auth_message[1]
print ' '
