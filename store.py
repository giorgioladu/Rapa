#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  store.py                                          # # # # # # # # # #
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

from django.conf import settings

try:
    # Django versions >= 1.9
    from django.utils.module_loading import import_module
except ImportError:
    # Django versions < 1.9
    from django.utils.importlib import import_module

SESSION_ENGINE = 'django.contrib.sessions.backends.file'
SESSION_EXPIRY = 720 #12h

def store():
    settings.configure()
    settings.SESSION_ENGINE = SESSION_ENGINE
    engine = import_module(settings.SESSION_ENGINE)
    store = engine.SessionStore()
    store.set_expiry(SESSION_EXPIRY)
    return store


def store_key(session_key):
    settings.configure()
    settings.SESSION_ENGINE = SESSION_ENGINE
    engine = import_module(settings.SESSION_ENGINE)
    store = engine.SessionStore(session_key)
    return store
