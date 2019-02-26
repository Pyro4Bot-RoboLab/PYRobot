#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
"""PYRO4BOT Launcher.

Launcher file
"""
import sys
import os
import json
import time
from termcolor import colored
import setproctitle

def get_PYRO4BOT_HOME():
    """ It turns back the environment path of the program Pyro4Bot """
    if "PYRO4BOT_HOME" not in os.environ:
        print("ERROR: PYRO4BOT_HOME not setted")
        print("please type export PYRO4BOT_HOME=<DIR> to set it up")
        sys.exit()
    else:
        return os.environ["PYRO4BOT_HOME"]


PYRO4BOT_HOME = get_PYRO4BOT_HOME()
print(PYRO4BOT_HOME)
sys.path.append(PYRO4BOT_HOME)

from node.libs.terminal import Terminal
from node import robotstarter as robot
from node.libs import utils
import components
import services
NAME_ROBOT = "<robot>"
if __name__ == "__main__":
    try:
        while True:
            jsonbot = os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "model", NAME_ROBOT + ".json"))
            PROCESS = robot.starter(filename=jsonbot,params={})
            setproctitle.setproctitle("PYRO4BOT." + PROCESS[0] + "." + "Console")
            #ROB = utils.get_pyro4proxy(PROCESS[1], PROCESS[0])

            Terminal(PROCESS[0],PROCESS[1],pid=PROCESS[3])

    except IOError:
        print("The file can not be found: %s" % jsonbot)
    except (KeyboardInterrupt, SystemExit):
        time.sleep(1)
        os._exit(0)
    except Exception:
        raise
