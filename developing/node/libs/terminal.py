from termcolor import colored
import time
from types import FunctionType
import os
import sys, io
import Pyro4
from node.libs import utils, botlogging

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import confirm, yes_no_dialog
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter

DEFAULT_BB_PASSWORD = "PyRobot"


def get_methods(cls):
    return [x for x, y in cls.__dict__.items() if type(y) == FunctionType and x[0] != "_"]


def get_elements(cls):
    return [x for x, y in cls.__dict__.items() if
            type(y) == Pyro4.core.Proxy and x[0] != "_" and x != "robot" and x != cls.name]


class Terminal(object):
    """
    terminal para rellenar
    """

    def __init__(self, name, uri, pid=None):
        self.exit = True
        self.robot = utils.get_pyro4proxy(uri, name)
        self.name = name
        setattr(self, name, self.robot)

        self.uri = uri
        self.pid = pid
        self.TTY = utils.get_tty()
        self._get_proxys()

        self.methods = get_methods(Terminal)
        self._all_methods = []
        self._indexing_methods_()
        self._control()

    def _indexing_methods_(self):
        elements = get_elements(self)
        methods = self.methods.copy()
        stdout_ = sys.stdout
        sys.stdout = io.StringIO()
        for el in elements:
            methods.append(el)
            sal = eval("self." + el + ".__docstring__()")
            for k, v in sal.items():
                print(k)
                methods.append((el + '.' + k))
        sys.stdout = stdout_
        self._all_methods = methods

    def _control(self):
        time.sleep(1)
        completer = WordCompleter(words=self._all_methods, ignore_case=True)
        while self.exit:
            self.prompt = "{} ".format(str(self.uri) + ">>")
            cad = prompt(self.prompt, history=FileHistory('history.txt'), completer=completer)
            args = cad.lower().split(" ")
            command = args[0]
            if command.split(".")[0] in self.__dict__:
                args.append(command)
                command = "run"
            if command in self.methods:
                eval("self." + command + "(*args)")
            else:
                print("command {} not found".format(command))

    def _get_proxys(self):
        proxys = [x for x in self.robot.get_uris(True) if isinstance(x, str)]
        for p in proxys:
            con = p.split("@")[0].split(".")[1]
            name = p.split("@")[0].split(".")[0].split(":")[1]
            proxy = utils.get_pyro4proxy(p, name)
            setattr(self, con, proxy)

    def help(self, *args):
        """ show information about command
            Usage:
                help <command>
                help
        """
        try:
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
        if confirm(message="Are you sure you want to shutdown?"):
            self.robot.shutdown()
            try:
                os.kill(self.pid, 9)
            except:
                print("Error: no PID available")
            exit()

    def status(self, *args):
        """ List all process started"""
        self.robot.print_process()

    def quit(self, *args):
        """ exit from terminal without killing services and components"""
        print("Quitting this way will not kill all the services and components")
        if confirm(message="Are you sure you want to quit?"):
            self.exit = False
            exit()

    def doc(self, *args):
        for k, v in self.robot.__docstring__().items():
            print(k)
            print("\t" + str(v))

    def run(self, *args):
        """
        run <component method> execute a class method
        """
        try:
            if args[0] == args[-1]:
                args = args[:-1]
            args = "".join(args).replace(", ", ",").replace("run", "")
            sal = eval("self." + args)
            print(colored("Running {}: ".format(args), 'green'))
            print(sal)
        except Exception as e:
            print("error ", args)
            print(e)

    def info(self, *args):
        """
        Get information about exposed methods in service or component
        """
        if len(args) == 2:
            try:
                sal = eval("self." + args[1] + ".__docstring__()")
                print(colored("methods information about {}: ".format(args[1]), 'green'))
                for k, v in sal.items():
                    print(colored(k, 'cyan'))
                    print("\t\t" + str(v))

            except Exception as e:
                print("error ", args[1])
        else:
            print("Error: type info <object>")

    def tty(self, *args):
        print(colored("Getting... type enter to exit", "cyan"))
        time.sleep(2)
        for c in args[1::]:
            sal = eval("self.{}.set_tty_out('{}')".format(c, self.TTY))
        wait = input("")
        for c in args[1::]:
            sal = eval("self.{}.set_tty_out()".format(c))

    def reboot(self, *args):
        if confirm(message="Are you sure you want to reboot?"):
            self.exit = False
            self.robot.shutdown()
            os.kill(self.pid, 9)
            time.sleep(2)
