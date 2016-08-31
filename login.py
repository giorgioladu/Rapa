# -*- coding: utf-8 -*-
#
#  login.py                                          # # # # # # # # # #
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
 
import pyrad.packet, cgi, sys, time
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import store
import html_page

form = cgi.FieldStorage()
mac = form.getvalue("mac")
ip = form.getvalue("ip")
gw_address = form.getvalue("gw_address","192.168.1.1")
gw_port = form.getvalue("gw_port","2060")
gw_id = form.getvalue("gw_id","WifiDog")
url = form.getvalue("url","www.google.com")
token = form.getfirst("token",None)# None
user = form.getfirst("username",None)# None
passwd = form.getfirst("password",None)# None


server = "192.168.0.1"
secret = "z87YAUJUfU4DQ"

srv=Client(server = server,
           secret = secret,
           dict=Dictionary("dictionary"))

def SendPacket(srv, req):
    try:
        return srv.SendPacket(req)
    except pyrad.client.Timeout:
        html_page.error_page( "RADIUS server does not reply")
        sys.exit(1)
    except socket.error, error:
        html_page.error_page( "Network error: " + str(error[1]) )
        sys.exit(1)

def auth(username, password):
    store_data = store.store()
    store_data.create()
    store_data["auth"] = False
    token = store_data.session_key     
    req=srv.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=username)
    req["Acct-Status-Type"]   = "Start"
    req["User-Password"]      = req.PwCrypt(password)
    req["NAS-IP-Address"]     = server
    req["NAS-Port-Type"]      = "Wireless-802.11"
    req["NAS-Port"]           = 0
    req["NAS-Identifier"]     = server
    req["Acct-Session-Id"]    = token
    req["Called-Station-Id"]  = gw_id
    req["Service-Type"]  = 1
    req["Acct-Delay-Time"]  = 0

    #req["FreeRADIUS-Stats-Start-Time"]  = time.strftime("%Y-%m-%d %H:%M")
    # 0 - AUTH_DENIED - User firewall users are deleted and the user removed.
    # 6 - AUTH_VALIDATION_FAILED - User email validation timeout has occured and user/firewall is deleted
    # 1 - AUTH_ALLOWED - User was valid, add firewall rules if not present
    # 5 - AUTH_VALIDATION - Permit user access to email to get validation email under default rules
    # -1 - AUTH_ERROR - An error occurred during the validation process
    reply=SendPacket(srv=srv, req=req)
    auth_message = reply.code    
    if reply.code==pyrad.packet.AccessAccept:
        store_data["auth"] = True
        store_data["username"] = username
        store_data["password"] = password
        store_data["last_incoming"] = "0"
        store_data["last_outgoing"] = "0"
        store_data["session_start"] = time.time()
        store_data["auth_message"]  = " User Access Accept "
        store_data["auth_response"]  = reply.code
    elif reply.code==pyrad.packet.AccessReject:
        store_data["auth_message"]  = " User Access Reject "
        store_data["auth_response"]  = reply.code
    else:
        store_data["auth_message"]  = " An error occurred during the validation process "
        store_data["auth_response"]  = reply.code
    store_data.save()
    return store_data

def login_page():
 html_page.header_page()
 print """ 
 
 <div class="login">
    <h1>Login</h1>
    <form method="post" action="login.py">
        <input type="text" id="username" name="username" placeholder="Username" required="required" />
        <input type="password" id="password" name="password" placeholder="Password" required="required" />"""
 print '<input type="hidden" id="gw_address" name="gw_address" value="'+str(gw_address) +'"/>' 
 print '<input type="hidden" id="gw_port" name="gw_port" value="'+str(gw_port) +'"/>' 
 print '<input type="hidden" id="gw_id" name="gw_id" value="'+str(gw_id) +'"/>' 
 print '<input type="hidden" id="mac" name="mac" value="'+str(mac) +'"/>' 
 print '<input type="hidden" id="url" name="url" value="'+str(url) +'"/>' 
 print """<br>
     <button type="submit" class="btn btn-primary btn-block btn-large">Let me in.</button>
     </form>
</div> 
 """
 html_page.footer_page()

if(gw_address and gw_id and mac):
    if (user and passwd ):
        user = cgi.escape(user)
        passwd = cgi.escape(passwd)
        store_data = auth(user,passwd)
        if store_data["auth"]:
            store_data["username"] = user 
            store_data["password"] = passwd
            token = store_data.session_key
            store_data["ip"] = ip
            store_data["mac"] = mac
            store_data["gw_address"] = gw_address
            store_data["gw_port"] = gw_port
            store_data["gw_id"] = gw_id
            store_data["token"] = token
            store_data["url"] = url
            store_data.save()            
            tokenurl = "http://"+str(gw_address)+':'+str(gw_port)+ "/wifidog/auth?token=" +str(token)
            print 'Status: 302 Found'
            print 'Location: '+tokenurl
            print ''
        else:
         html_page.error_page(store_data["auth_message"])
    else:
      login_page()
else:
 html_page.error_page("BUMP!!")


    







