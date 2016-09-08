#!/usr/bin/env python
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
## 08.09.2016 V. 1.08
##

import pyrad.packet
import cgi
import sys
import time
from pyrad.client import Client
from pyrad.dictionary import Dictionary
import store
import html_page
import config

form = cgi.FieldStorage()
mac = form.getvalue("mac", "00:00:00:00")
ip = form.getvalue("ip","0.0.0.0")
gw_address = form.getvalue("gw_address",config.node_ip)
gw_port = form.getvalue("gw_port",config.node_port)
gw_id = form.getvalue("gw_id",config.node_name)
url = form.getvalue("url",config.custom_url )
token = form.getfirst("token", None)  # None
user = form.getfirst("username")
passwd = form.getfirst("password")


ACCOUNT_STATUS_ERROR = -1
ACCOUNT_STATUS_DENIED = 0
ACCOUNT_STATUS_ALLOWED = 1
ACCOUNT_STATUS_VALIDATION = 5
ACCOUNT_STATUS_VALIDATION_FAILED = 6
ACCOUNT_STATUS_LOCKED = 254

radius_config = {
    'server': config.radius_server,  # radius server
    'secret': config.radius_secret ,  # radius secret key
    'dict': Dictionary(config.radius_dictionary),
}

srv = Client(**radius_config)


def SendPacket(srv, req):
    try:
        return srv.SendPacket(req)
    except pyrad.client.Timeout:
        html_page.error_page("RADIUS server does not reply")
        sys.exit(1)
    except socket.error as error:
        html_page.error_page("Network error: " + str(error[1]))
        sys.exit(1)


def auth(username, password):
    store_data = store.store()
    store_data.create()
    store_data["auth"] = False
    token = store_data.session_key
    req = srv.CreateAuthPacket(
        code=pyrad.packet.AccessRequest,
        User_Name=username)
    req["Acct-Status-Type"] = "Start"
    req["User-Password"] = req.PwCrypt(password)
    req["NAS-IP-Address"] = gw_address
    
    req["NAS-Port"] = config.custom_nas_port
    req["NAS-Port-Type"] = config.custom_nas_port_type
    
    req["NAS-Identifier"] =  gw_id
    req["Acct-Session-Id"] = token
    req["Service-Type"] =  pyrad.packet.AccessRequest
    req["Acct-Delay-Time"] = 0
    req["Framed-IP-Address"] = ip
    
    req["Called-Station-Id"] = config.node_mac #MAC OF WIFIDOG"00-10-A4-23-19-C0"
    req["Calling-Station-Id"] = mac #MAC OF USER OR IP "00-00-B4-23-19-C0"
    reply = SendPacket(srv=srv, req=req)
    auth_message = reply.code
    
    if reply.code == pyrad.packet.AccessAccept:
        store_data["auth"] = True
        store_data["username"] = username
        store_data["password"] = password
        store_data["session_start"] = time.time()
        store_data["auth_message"] = " User Access Accept "
        store_data["auth_response"] = reply.code
        for i in reply.keys():
            store_data[i] = reply[i][0]
    elif reply.code == pyrad.packet.AccessReject:
        store_data["auth_message"] = " User Access Reject "
        store_data["auth_response"] = reply.code
    else:
        store_data[
            "auth_message"] = " An error occurred during the validation process "
        store_data["auth_response"] = reply.code
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
    print '<input type="hidden" id="gw_address" name="gw_address" value="' + str(gw_address) + '"/>'
    print '<input type="hidden" id="gw_port" name="gw_port" value="' + str(gw_port) + '"/>'
    print '<input type="hidden" id="gw_id" name="gw_id" value="' + str(gw_id) + '"/>'
    print '<input type="hidden" id="mac" name="mac" value="' + str(mac) + '"/>'
    print '<input type="hidden" id="url" name="url" value="' + str(url) + '"/>'
    print """<br>
     <button type="submit" class="btn btn-primary btn-block btn-large" class="rbutton" >Let me in.</button>
     </form>
     <script type="text/javascript">
    $('.rbutton').on('click',function() {
    $(this).prop("disabled",true);
});
    </script>
    </div>
 """
    html_page.footer_page()

if "generate_204" in url:
    print 'HTTP/1.1 204 No Content'
    print ''
    sys.exit(0)

if "success.html" in url:
    print 'HTTP/1.1 200 OK'
    print """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
        <HTML>
        <HEAD>
                <TITLE>Success</TITLE>
        </HEAD>
        <BODY>
        Success
        </BODY>
        </HTML>
  """
    print ''
    sys.exit(0)

if url.find("ncsi.txt") != -1:
    print 'HTTP/1.1 200 OK'
    print 'Microsoft NCSI'
    print ''
    sys.exit(0)

if url.find("connect") != -1:
    print 'HTTP/1.1 200 OK'
    print 'OK'
    print ''
    sys.exit(0)

if(gw_address and gw_id and mac):
    if (user and passwd):
        user = cgi.escape(user)
        passwd = cgi.escape(passwd)
        store_data = auth(user, passwd)
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
            tokenurl = "http://" + str(gw_address) + ':' + str(
                gw_port) + "/wifidog/auth?token=" + str(token)
            print 'HTTP/1.1 302 Found'
            print 'Location: ' + tokenurl
            print ''
        else:
            html_page.error_page(store_data["auth_message"])
    else:
        login_page()
else:
    html_page.error_page("BUMP!!")
