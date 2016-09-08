#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  ping.py                                           # # # # # # # # # #
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
# 08.09.2016 V. 1
##


import ConfigParser, os

config = ConfigParser.ConfigParser()
config.read('rapa.cnf')

mysql_server = config.get('Mysql', 'server')
mysql_port = config.get('Mysql', 'port')
mysql_user = config.get('Mysql', 'user')
mysql_password = config.get('Mysql', 'password')
mysql_database = config.get('Mysql', 'DB')
mysql_database_table = config.get('Mysql', 'table')

node_latitude = config.get('Node', 'latitude')
node_longitude = config.get('Node', 'longitude')
node_mac = config.get('Node', 'mac')
node_name = config.get('Node', 'name')
node_ip = config.get('Node', 'ip')
node_port = config.get('Node', 'port')

radius_server = config.get('Radius', 'server')
radius_secret = config.get('Radius', 'secret')
radius_dictionary = config.get('Radius', 'dictionary')

custom_url = config.get('Custom', 'url')
custom_nas_port = config.get('Custom', 'nas_port')
custom_nas_port_type = config.get('Custom', 'nas_port_type')


