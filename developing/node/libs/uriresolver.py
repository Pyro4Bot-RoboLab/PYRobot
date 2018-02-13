#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# All datas defined in json configuration are atributes in your code object
import time
from node.libs import control, utils
import Pyro4
from termcolor import colored
import threading
import os
import sys
ROUTER_PASSWORD = "PyRobot"
ROUTER_IP = "192.168.10.1"
ROUTER_PORT = "6060"


class uriresolver(control.Control):
    @control.load_config
    def __init__(self, robot, password="default"):
        # Atributes
        Pyro4.config.HOST = "localhost"
        self.botName = robot["name"]  # Robot's Name
        self.port = robot["port_node"]
        self.start_port = robot["start_port"]
        self.port_ns = robot["port_ns"]
        self.ip = robot["ip"]

        self.URIS = {}

        # NameServer
        self.nameserver = None  # Local, NameServer or BigBrother location
        self.usingBB = False

        # DaemonProxy
        self.daemonproxy = None  # Proxy object
        self.uri = None  # Uriresolver uri on proxy
        self.password = password
        self.thread_proxy = threading.Thread(
            target=self.create_uriresolver_proxy, args=())
        # self.thread_proxy.setDaemon(1)
        self.thread_proxy.start()

        self.get_ns()

    def create_uriresolver_proxy(self):
        try:
            Pyro4.config.HOST = "localhost"
            Pyro4.config.SERIALIZERS_ACCEPTED = set(
                ['pickle', 'json', 'marshal', 'serpent'])
            self.port = utils.get_free_port(self.port)
            self.daemonproxy = Pyro4.Daemon(
                host="127.0.0.1", port=self.port)  # Daemon proxy for NODE
            self.daemonproxy._pyroHmacKey = bytes(self.password)
            self.daemonproxy.requestLoop()
        except Pyro4.errors.ConnectionClosedError:
            print("Error al conectar al proxy")
        except Exception:
            print("ERROR: creating nodeProxy")
        finally:
            if (self.uri is not None):
                print("[%s] Shutting %s" %
                      (colored("Down", 'green'), self.uri.asString()))
            os._exit(0)

    def register_uriresolver(self):
        attempts = 0
        while not (self.daemonproxy):
            time.sleep(0.3)
            if attempts is 10:
                break
            attempts += 1
        try:
            Pyro4.config.HOST = "localhost"
            name = self.botName + ".URI_resolv"
            # Registering uriresolver
            self.uri = self.daemonproxy.register(self, objectId=name)
            # Getting proxy
            self.proxy = Pyro4.Proxy(self.uri)
            self.proxy._pyroHmacKey = bytes(self.password)
        except Exception:
            print("ERROR: register_uriresolver in uriresolver.py")

        connect = False
        while not connect:
            try:
                connect = self.proxy.echo() == "hello"
            except Exception:
                connect = False
            time.sleep(0.3)
        if connect:
            print(
                colored("___________STARTING RESOLVER URIs___________________",
                        "yellow"))
            print("URI %s" % colored(self.uri.asString(), 'green'))

            if self.get_ns():
                print("NAME SERVER LOCATED. %s" %
                      (colored(" Resolving remote URIs ", 'green')))
            else:
                print("NAME SERVER NOT LOCATED. %s" %
                      (colored(" Resolving only LOCAL URIs ", 'green')))
            return self.uri, self.proxy
        else:
            print("Cant connect with uriresolver")
            return None

    @Pyro4.expose
    def get_ns(self):
        if self.nameserver is None:
            if (utils.ping(ROUTER_IP)):
                # Looking for BigBrother
                try:
                    Pyro4.config.HOST = str(ROUTER_IP)
                    self.nameserver = Pyro4.Proxy(
                        "PYRO:bigbrother@" + ROUTER_IP + ":" + ROUTER_PORT)
                    self.nameserver._pyroHmacKey = bytes(ROUTER_PASSWORD)
                    if (self.nameserver.ready()):
                        printInfo("BIGBROTHER ----> PYRO:bigbrother@" +
                                  ROUTER_IP + ":" + ROUTER_PORT)
                        self.usingBB = True
                except Exception:
                    printInfo("BigBrother error.", "red")
                    self.nameserver = None
            else:
                self.nameserver = None
                printInfo("BigBrother not found.", "red")

        if self.nameserver is None:
            # Looking for Network NameServer
            try:
                self.nameserver = Pyro4.locateNS()
                printInfo("Nameserver located")
                self.nameserver.ping()
            except Exception:
                printInfo("NameServer not found.", "red")
                self.nameserver = None

        if self.nameserver is None:
            # Creating a NameServer
            try:
                port = utils.get_free_port(self.port_ns, ip=self.ip)
                self.nsThread = threading.Thread(
                    target=Pyro4.naming.startNSloop,
                    kwargs={'host': self.ip, 'port': port})
                self.nsThread.start()
                time.sleep(1)
                printInfo("NameServer created.")
            except Exception:
                printInfo("Error creating NameServer", "red")
                self.nameserver = None

            # Locate NS
            attempts = 0
            while attempts < 10:
                try:
                    self.nameserver = Pyro4.locateNS()
                    self.nameserver.ping()
                    break
                except Exception:
                    attempts += 1
                    time.sleep(0.3)
        return self.nameserver if self.nameserver else None

    def ns_ready(self):
        if (self.nameserver is None):
            return None
        return self.nameserver.ready()

    def get_proxy_without_uri(self, obj, passw=None):
        target = obj.split(".")
        if (target[0] and target[1] and
                target[0].count("*") == 0 and
                target[1].count("*") == 0):
            if (passw is None):
                passw = target[0]
            try:
                proxy = utils.get_pyro4proxy(
                    self.nameserver.lookup(target[0]), passw)
                bot_uris = proxy.get_uris()
                for x in bot_uris:
                    (name, ip, port) = utils.uri_split(x)
                    if (name.split(".")[1] == target[1]):
                        proxy = utils.get_pyro4proxy(x, passw)
                        return proxy
            except Exception:
                print "Error al resolver ", obj
        else:
            if (self.usingBB):
                self.nameserver.proxy(target, passw)
            else:
                print "Para usar esta funcionalidad se necesita de BigBrother"
                return None

    @Pyro4.expose
    def get_proxy(self, obj, passw=None):
        print "get_proxy", obj
        if (self.nameserver):
            try:
                # PYRO:simplebot.infrared@192.168.10.67:6001
                if (obj.count('PYRO:') == 1 and obj.count('@') == 1 and
                        obj.count(":") == 2 and obj.count(".") in range(3, 5)):
                            (name, _, _) = utils.uri_split(obj)
                            if ("." in name):
                                name = name.split(".")[0]
                            if (passw is None):
                                passw = name
                            return utils.get_pyro4proxy(obj, passw)
                elif (obj.count(".") == 1):  # simplebot.sensor
                    return (self.get_proxy_without_uri(obj, passw))
                else:
                    print "Objeto no valido"
            except Exception:
                return None

    @Pyro4.expose
    def new_uri(self, name, mode="public"):
        if mode == "local":
            ip = "127.0.0.1"
        else:
            ip = self.ip

        port_node = utils.get_free_port(self.port, interval=10)
        start_port = utils.get_free_port(self.start_port)

        if name.find(self.botName) > -1:
            if name != self.botName:
                uri = "PYRO:" + name + "@" + ip + ":" + str(start_port)
            else:
                uri = "PYRO:" + name + "@" + ip + ":" + str(port_node)
        else:
            uri = "PYRO:" + name + "@" + self.ip + ":" + str(start_port)

        self.URIS[name] = uri
        self.start_port = start_port + 1
        self.port_node = port_node + 1
        return uri

    @Pyro4.expose
    def get_uri(self, name):
        if self.URIS.has_key(name):
            return self.URIS[name]
        else:
            return None

    @Pyro4.expose
    def get_name(self, uri):
        for k, v in self.URIS.iteritems():
            if v == uri:
                return k
        return None

    @Pyro4.expose
    def wait_available(self, uri, password, trys=20):
        # eso puede ser asinc return
        connect = False
        if uri.find("@") == -1:
            uri = self.get_uri(uri)
        try:
            p = Pyro4.Proxy(uri)
            p._pyroHmacKey = bytes(password)
        except:
            return None
        while not connect and trys > 0:
            trys = trys - 1
            try:
                connect = p.echo() == "hello"
            except:
                connect = False
            time.sleep(0.2)
        if connect:
            return uri
        else:
            return None

    @Pyro4.expose
    def wait_resolv_remotes(self, name, trys=10):
        connect = False
        if not self.nameserver:
            return None
        while not connect and trys > -1:
            try:
                getbot = self.nameserver.lookup(name[0:name.find(".")])
                proxy = Pyro4.Proxy(getbot)
                proxy._pyroHmacKey = bytes(password)
                remoteuri, status = proxy.get_name_uri(name)
                connect = (remoteuri != None and status not in [
                           "down", "wait"])
            except:
                # print "error remote"
                pass
            trys -= 1
            time.sleep(0.05)
        if trys < 0:
            return name
        if connect:
            return remoteuri

    @Pyro4.expose
    def register_robot_on_nameserver(self, uri):
        try:
            if self.nameserver is not None:
                # print "___________REGISTERING PYRO4BOT ON NAME SERVER_________________"
                self.URIS[self.botName] = uri
                print("REGISTERING ROBOT URI: %s" %
                      (colored(self.URIS[self.botName], 'green')))
                if (self.usingBB):
                    self.nameserver.register(
                        self.botName, self.URIS[self.botName])
                else:
                    nserver = Pyro4.locateNS()
                    nserver.register(self.botName, self.URIS[self.botName])
            else:
                print(colored("NAME SERVER NOT FIND", 'red'))

        except Exception:
            print("ERROR:name server not find")
            raise

    @Pyro4.expose
    def list_uris(self, node=False):
        if node:
            return [self.URIS[x] for x in self.URIS]
        else:
            return [self.URIS[x] for x in self.URIS if x.find(".") > -1 and self.URIS[x].find("127.0.0.1") is -1]



def printInfo(text, color="green"):
    print colored("[uriresolver]:" + text, color)


if __name__ == "__main__":
    pass