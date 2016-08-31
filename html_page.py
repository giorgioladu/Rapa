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
 
def header_page():
 print 'Content-type: text/html'
 print
 print """
  <!DOCTYPE html>
   <html >
  <head>
    <meta charset="UTF-8">
    <title>Login Form</title>  
    <link rel="stylesheet" href="css/style.css">
  </head><body> """

def footer_page():
 print """
        <script src="js/index.js"></script>
        </body></html>"""


def error_page(message):
 print 'Content-type: text/html'
 print
 print """
  <!DOCTYPE html>
  <html >
  <head>
    <meta charset="UTF-8">
    <title>Login Error</title>      
  </head><body>"""
 print '<h1>'+str (message) +'</h1>'
 footer_page()

def html_page(message):
 header_page()
 print str (message)
 footer_page()
