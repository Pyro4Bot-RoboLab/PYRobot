#!/usr/bin/env python
"""PYRO4BOT Launcher.

Launcher file
"""
import sys
import os


def get_PYRO4BOT_HOME():
    if "PYRO4BOT_HOME" not in os.environ:
        print("PYRO4BOT_HOME not set")
        print("please type export PYRO4BOT_HOME=<DIR> to set ")
        sys.exit()
    else:
        return os.environ["PYRO4BOT_HOME"]


PYRO4BOT_HOME = get_PYRO4BOT_HOME()
sys.path.append(PYRO4BOT_HOME)

from node import robotstarter as robot
import setproctitle
from node.libs import utils
import time
from termcolor import colored

if __name__ == "__main__":
    try:
        jsonbot = "./model/<robot>"

        PROCESS = robot.starter(filename=jsonbot)

        setproctitle.setproctitle("PYRO4BOT." + PROCESS[0] + "." + "Console")
        ROB = utils.get_pyro4proxy(PROCESS[1], PROCESS[0])

        salir = True
        time.sleep(2)
        while salir:
            print(colored("\n----\nAvailable commands:: \n* Doc \n* Status \n* Exit\n----\n", "green"))
            cad = input("{} ".format(colored(PROCESS[0] + ":", 'green')))
            if cad.upper() == "EXIT":
                ROB.shutdown()
                os.kill(PROCESS[3], 9)
                exit()
            if cad.upper() == "STATUS":
                ROB.print_process()
            if cad.upper() == "DOC":
                for k, v in ROB.__docstring__().items():
                    print(k)
                    print("\t" + str(v))
            if cad.upper() == "SALIR":
                salir = False
                exit()
    except IOError:
        print("The file can not be found: %s" % jsonbot)
    except (KeyboardInterrupt, SystemExit):
        os._exit(0)
    except Exception:
        raise
