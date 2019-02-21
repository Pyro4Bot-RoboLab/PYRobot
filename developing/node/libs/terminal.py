from termcolor import colored
import time
from types import FunctionType
import os
import Pyro4
from node.libs import utils

DEFAULT_BB_PASSWORD = "PyRobot"


def methods(cls):
    return [x for x, y in cls.__dict__.items() if type(y) == FunctionType and x[0] != "_"]


class Terminal(object):
    def __init__(self, ROB, PROCESS):
        self.exit = True
        self.robot = ROB
        self.process = PROCESS
        self.methods = methods(Terminal)
        self._get_proxyes()
        self._control()

    def _control(self):
        time.sleep(1)
        print(colored("Type help for show commands"))
        while self.exit:
            cad = input("{} ".format(colored(str(self.process[1]) + ">>", 'green')))
            args = cad.lower().split(" ")
            command = args[0]
            if command in self.methods:
                eval("self." + command + "(*args)")
            else:
                print("command {} not found".format(command))

    def _get_proxyes(self):
        proxys = self.robot.get_uris()
        for p in proxys:
            con = p.split("@")[0].split(".")[1]
            name = p.split("@")[0].split(".")[0].split(":")[1]
            print(con, name)
            proxy = utils.get_pyro4proxy(p, name)
            setattr(self, con, proxy)

    def help(self, *args):
        """ show information about command
            Usage:
                help <command>
                help
        """
        try:
            print(self.methods)
            if len(args) <= 1:
                for f in self.methods:
                    print("command {}:".format(f))
                    print(eval("self." + f + ".__doc__"))
            else:
                print("Command {} :".format(args[1]))
                print(eval("self." + args[1] + ".__doc__"))
        except:
            print("error ", args)
            raise

    def shutdown(self, *args):
        """ exit from terminal killing all services and components"""
        self.robot.shutdown()
        os.kill(self.process[3], 9)
        exit()

    def status(self, *args):
        """ List all process started"""
        self.robot.print_process()

    def quit(self, *args):
        """ exit from terminal without killing services and components"""
        self.exit = False
        exit()

    def doc(self, *args):
        for k, v in self.robot.__docstring__().items():
            print(k)
            print("\t" + str(v))

    def run(self, *args):
        try:
            sal = eval("self." + args[1])
            print(colored("Running {}: ".format(args[1]), 'green'))
            print(sal)
        except:
            print("error ", args[1])
            raise
