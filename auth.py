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
 

import pyrad.packet, cgi, socket, sys, time
import cgitb; cgitb.enable()
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import store
import html_page

ACCOUNT_STATUS_ERROR = -1
ACCOUNT_STATUS_DENIED = 0
ACCOUNT_STATUS_ALLOWED = 1
ACCOUNT_STATUS_VALIDATION = 5
ACCOUNT_STATUS_VALIDATION_FAILED = 6
ACCOUNT_STATUS_LOCKED = 254

form = cgi.FieldStorage()
stage = form.getfirst("stage") # counters or login,logout
mac = form.getvalue("mac")
ip = form.getfirst("ip","0.0.0.0")
gw_address = form.getfirst("gw_address","0.0.0.0")
gw_port = form.getvalue("gw_port",0)
gw_id = form.getvalue("gw_id")
incoming = form.getvalue("incoming",0)
outgoing = form.getvalue("outgoing",0)
url = form.getvalue("url","http://www.google.com")
token = form.getfirst("token", None )
user = form.getfirst("username",None)
passwd = form.getfirst("password",None)

server = "192.168.0.1"
secret = "z87YAUJUfU4DQ"

auth_response = ACCOUNT_STATUS_DENIED
auth_message = ""


def SendPacket(srv, req):
    try:
        return srv.SendPacket(req)
    except pyrad.client.Timeout:
        html_page.error_page( "RADIUS server does not reply")
        sys.exit(1)
    except socket.error, error:
        html_page.error_page( "Network error: " + str(error[1]) )
        sys.exit(1)

srv=Client(server = server,
           secret = secret,
           dict=Dictionary("dictionary"))

if stage == "login" :
        store_data = store.store_key(token) 
        store_data["last_incoming"] = "0"
        store_data["last_outgoing"] = "0"
        store_data["session_start"] = time.time()
        req=srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=store_data["username"])
        req["Acct-Status-Type"]   = "Start"
        req["User-Password"]      = req.PwCrypt(store_data["password"])
        req["NAS-IP-Address"]     = server
        req["NAS-Port"]           = gw_port
        req["NAS-Port-Type"]      = "Wireless-802.11"
        req["NAS-Identifier"]     = server
        req["Acct-Session-Id"]    = token
        req["Called-Station-Id"]  = gw_id
        req["Framed-IP-Address"]  = ip
        req["Service-Type"]  = 1
        req["Acct-Delay-Time"]  = 0

        reply=SendPacket(srv, req)
        auth_message = reply.code    
        if reply.code==pyrad.packet.AccessAccept:        
            auth_response = ACCOUNT_STATUS_ALLOWED
            auth_message = " User is now log in ",reply.code
            store_data["auth"] = True
        elif reply.code==pyrad.packet.AccessReject:
            auth_message = " User Access Reject ",reply.code
            auth_response = ACCOUNT_STATUS_VALIDATION_FAILED
        else :
           auth_message = " An error occurred during the validation process ", reply.code
           auth_response = ACCOUNT_STATUS_ERROR
        store_data.save()

if stage == "counters" :
    store_data = store.store_key(token)
    req = srv.CreateAcctPacket(User_Name=store_data["username"])
    req["Acct-Status-Type"]="Interim-Update"
    req["Acct-Session-Id"]    = token
    req["Framed-IP-Address"]= ip  
    OutputGiga = int(incoming) - int(store_data["last_incoming"])
    InputGiga = int(outgoing) - int(store_data["last_outgoing"])
    req["Acct-Input-Gigawords"] = abs(OutputGiga)
    req["Acct-Output-Gigawords"] = abs(InputGiga)
    store_data["last_incoming"] = incoming
    store_data["last_outgoing"] = outgoing
    reply = SendPacket(srv, req)
    auth_message = "Sending Alive packet", reply.code
    auth_response = ACCOUNT_STATUS_ALLOWED
    store_data.save()

if stage == "logout" :
    store_data = store.store_key(token)
    req = srv.CreateAcctPacket(User_Name=store_data["username"] )
    req["NAS-IP-Address"]     = server
    req["NAS-Port-Type"]      = "Wireless-802.11"
    req["NAS-Port"]           = gw_port
    req["Acct-Status-Type"]   = "Stop"
    req["Acct-Terminate-Cause"] = "User-Request"
    SessionTime = int(time.time() - store_data["session_start"])
    req["Acct-Session-Time"] = abs(SessionTime)
    req["NAS-Identifier"]     = server
    req["Acct-Session-Id"]    = token
    req["Called-Station-Id"]  = gw_id
    req["Framed-IP-Address"]  = ip
    OutputGiga = int(incoming) - int(store_data["last_incoming"])
    InputGiga = int(outgoing) - int(store_data["last_outgoing"])
    req["Acct-Input-Gigawords"] = abs(OutputGiga)
    req["Acct-Output-Gigawords"] = abs(InputGiga)
    store_data["last_incoming"] = incoming
    store_data["last_outgoing"] = outgoing

    reply = srv.SendPacket(req)
    auth_response = ACCOUNT_STATUS_ALLOWED
    auth_message = " User is now logged out ",reply.code
    store_data["auth"] = False
    #store_data.remove()
    store_data.save()


print "Auth:",auth_response," "
print "Messages:",auth_message[0],"\n"

