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
# 06.09.2016 V. 1.06
# * Added mysql

import MySQLdb
import cgi
import config

form = cgi.FieldStorage()
gw_wifidog_uptime = form.getvalue("wifidog_uptime", 0)
gw_sys_load = form.getvalue("sys_load", 0)
gw_sys_memfree = form.getvalue("sys_memfree", 0)  # gateway adress
gw_sys_uptime = form.getvalue("sys_uptime", 0)
gw_id = form.getvalue("gw_id", "gw_id")

print 'Pong'


database = MySQLdb.connect(
    host=config.mysql_server,
    port=int(
        config.mysql_port),
    user=config.mysql_user,
    passwd=config.mysql_password,
    db=config.mysql_database)

cursor = database.cursor()

sql = "UPDATE " + config.mysql_database_table + " SET `time`=NOW(),`uptime`=\"" + str(gw_sys_uptime) + "\" ,`memfree`=\"" + \
    str(gw_sys_memfree) + "\",`cpu`=\"" + str(gw_sys_load) + "\" WHERE `mac` = \"" + str(config.node_mac) + "\""

try:
    cursor.execute(sql)
    data = cursor.rowcount
    if (cursor.rowcount <= 0):
        sql = "INSERT INTO " + config.mysql_database_table + "  (`time`, `name`, `latitude`, `longitude`, `mac`, `uptime`, `memfree`, `cpu`) VALUES ( NOW() , \"" + str(config.node_name) + "\", \"" + str(
            config.node_latitude) + "\", \"" + str(config.node_longitude) + "\", \"" + str(config.node_mac) + "\", \"" + str(gw_sys_uptime) + "\", \"" + str(gw_sys_memfree) + "\", \"" + str(gw_sys_load) + "\" )"
        cursor.execute(sql)
        database.commit()
except MySQLdb.Warning as e:
    # Rollback in case there is any error
    print ""
finally:
    database.close()
