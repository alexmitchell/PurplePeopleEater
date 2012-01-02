#!/usr/bin/env python
from kxgames.core import *
import main

debugger = LoopDebugger()

import network_settings
network_settings.host = 'localhost'

debugger.loop("Server", main.ServerLoop())
debugger.loop("Client 1", main.UserLoop())
debugger.loop("Client 2", main.UserLoop())

debugger.run()
