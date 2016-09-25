# -*- coding: utf-8 -*-
#
#  html_page.py                                      # # # # # # # # # #
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
import config

def header_page():
    #print 'Content-type: text/html'
    print
    print """
  <html class="no-js">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="profile" href="http://gmpg.org/xfn/11" />
        
        <title>Login Form </title>
        
      <!-- Open Graph -->
        <meta property="og:site_name" content="HotSpot Login" />
        <meta property="og:description" content="HotSpot Login" />
		<meta property="og:type" content="website" /> 

        <!-- Icons -->
        <link rel="icon" href="favicon.ico" type="image/png">
		
        
        <!-- Styles  -->
        <link href="css/style.css"  rel="stylesheet">
        <link href="css/font-awesome.min.css" rel="stylesheet">
        <link href="css/bootstrap.min.css" rel="stylesheet">
            
      </head>
    <body>

   """


def footer_page():
    print """
    <div class="alert alert-info" role="alert"> 
    <strong> All rights reserved. <i class="fa fa-copyright" aria-hidden="true"></i> 
    &nbsp; &sdot; &nbsp; Powered by <a href="https://github.com/giorgioladu/Rapa" > R.A.Pa </strong>  </a>
    &nbsp;&sdot;&nbsp; Design by
    <a href="https://www.facebook.com/giorgio.ladu" aria-label="giorgio.ladu">
	 <i class="fa fa-facebook-square m-blau" aria-hidden="true"></i>
	</a>            
      <a href="https://www.facebook.com/giorgio.ladu" >Giorgio Ladu</a>
    """
    print config.custom_footer_html_message
    print """     </div>
        <script src="js/index.js"></script>
        </body></html>"""


def error_page(message):
    #print 'Content-type: text/html'
    print
    print """
    <html class="no-js">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="profile" href="http://gmpg.org/xfn/11" />
        
        <title>Login Error </title>
        
      <!-- Open Graph -->
        <meta property="og:site_name" content="HotSpot Login" />
        <meta property="og:description" content="HotSpot Login" />
		<meta property="og:type" content="website" /> 

        <!-- Icons -->
        <link rel="icon" href="favicon.ico" type="image/png">
		
        
        <!-- Styles  -->
        <link href="css/style.css"  rel="stylesheet">
        <link href="css/font-awesome.min.css" rel="stylesheet">
        <link href="css/bootstrap.min.css" rel="stylesheet">
               
      </head>
    <body>
    <div class="alert alert-danger" role="alert">
  <strong>Login Error</strong> 
  <br>
  """
    print '<h3>' + str(message) + '</h3><br></div>'
    footer_page()

def success_apple():
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
    

def html_page(message):
    header_page()
    print str(message)
    footer_page()
