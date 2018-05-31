import Pyro4
import utils
import time
import token
import threading
from threading import Thread
from termcolor import colored
from botlogging import botlogging

SECS_TO_CHECK_STATUS = 5

# DECORATORS

# Threaded function snippet
def threaded(fn):
    """To use as decorator to make a function call threaded."""
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def load_config(in_function):
    """ Decorator for load Json options in Pyro4bot objects
        init superclass control """
    def out_function(*args, **kwargs):
        _self = args[0]
        try:
            _self.DATA = args[1]
        except Exception:
            pass
        _self.__dict__.update(kwargs)
        super(_self.__class__.__mro__[0], _self).__init__()
        in_function(*args, **kwargs)
    return out_function


def Pyro4bot_Loader(clss, **kwargs):
    """ Decorator for load Json options in Pyro4bot objects
        init superclass control
    """
    original_init = clss.__init__
    def init(self):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super(clss, self).__init__()
        original_init(self)
    clss.__init__ = init
    return clss


def flask(*args_decorator):
    def flask_decorator(func):
        original_doc = func.__doc__
        if func.__doc__ is None:
            original_doc = ""
        if len(args_decorator) % 2 == 0:  # Tuplas
            for i in xrange(0, len(args_decorator), 2):
                original_doc += "\n@type:" + \
                    args_decorator[i] + "\n@count:" + \
                    str(args_decorator[i + 1])
        elif len(args_decorator) == 1:
            original_doc += "\n @type:" + \
                args_decorator[0] + "\n@count:" + \
                str(func.__code__.co_argcount - 1)

        if "@type:actuator" in original_doc:
            li = list(func.__code__.co_varnames)
            del li[0]
            original_doc += "\n@args_names:" + str(li)

        func.__doc__ = original_doc

        def func_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        func_wrapper.__doc__ = original_doc
        return func_wrapper
    return flask_decorator


def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
        return ret
    return wrap


class Control(botlogging.Logging):
    """ This class provide threading funcionality to all object in node.
        Init workers Threads and PUB/SUB thread"""

    def __init__(self):
        super(Control,self).__init__()
        self.mutex = threading.Lock()
        self.workers = []
        if "worker_run" not in self.__dict__:
            self.worker_run = True

    def __check_start__(self):
        while (self._REMOTE_STATUS != "OK" or
               (self._REMOTE_STATUS == "ASYNC" and
                not self._resolved_remote_deps)):
            time.sleep(SECS_TO_CHECK_STATUS)

    @threaded
    def init_workers(self, fn, *args):
        """ Start all workers daemon"""
        self.__check_start__()
        if type(fn) not in (list, tuple):
            fn = (fn,)
        if self.worker_run:
            for func in fn:
                t = threading.Thread(target=func, args=args)
                self.workers.append(t)
                t.setDaemon(True)
                t.start()

    @threaded
    def init_thread(self, fn, *args):
        """ Start all workers daemon"""
        self.__check_start__()
        if self.worker_run:
            t = threading.Thread(target=fn, args=args)
            self.workers.append(t)
            t.start()

    @threaded
    def init_publisher(self, token_data, frec=0.01):
        """ Start publisher daemon"""
        self.threadpublisher = False
        self.subscriptors = {}
        if isinstance(token_data, token.Token):
            self.threadpublisher = True
            t = threading.Thread(target=self.thread_publisher,
                                 args=(token_data, frec))
            self.workers.append(t)
            t.setDaemon(True)
            t.start()
        else:
            print(
                "ERROR: Can not publish to object other than token {}".format(token_data))

    def thread_publisher(self, token_data, frec):
        """Publish the token in the subscriber list."""
        self.__check_start__()
        while self.threadpublisher:
            d = token_data.get_attribs()
            try:
                for key in self.subscriptors.keys():
                    subscriptors = self.subscriptors[key]
                    try:
                        if key in d:
                            for item in subscriptors:
                                # print("publicando",key, d[key])
                                try:
                                    item.publication(key, d[key])
                                except (Pyro4.errors.ConnectionClosedError, Pyro4.errors.CommunicationError):
                                    print("Can not connect to the subscriber: {}".format(item))
                                    del self.subscriptors[key]
                                except Exception as ex:
                                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                                    print template.format(type(ex).__name__, ex.args)
                                    del self.subscriptors[key]

                    except TypeError:
                        print("Invalid argument.")
                        raise
                        exit()
            except Exception as e:
                print utils.format_exception(e)
                raise
            time.sleep(frec)

    @threaded
    def send_subscription(self, identifier, token, mypassword=None):
        """Send a subscription request to the object given by parameter."""
        try:
            t = threading.Thread(target=self.thread_subscriber,
                                 args=(identifier, token, mypassword))
            self.workers.append(t)
            t.start()
        except Exception:
            print "Error sending subscription"

    def thread_subscriber(self, identifier, token, mypassword=None):
        self.__check_start__()
        """Send a subscription request to the identifier given by parameter."""
        try:
            if (hasattr(self, identifier)):
                x = getattr(self, identifier)
                x.subscribe(token, self.pyro4id)
            else:
                connected = False
                while not connected:
                    if (identifier in self.deps):
                        try:
                            self.deps[identifier].subscribe(token, self.pyro4id, mypassword=mypassword)
                            print(colored("Subscribed to: {} with topic: {}".format(identifier, token), "green"))
                            connected = True
                        except Exception:
                            pass
                    time.sleep(2)
        except Exception:
            print("ERROR: in subscripcion to %s TOKEN: %s PASS: %s" % (identifier, token, mypassword))
            raise



    @Pyro4.expose
    def subscribe(self, identifier, uri, mypassword=None):
        """ Receive a request for subcripcion from an object and save data in dict subcriptors
            Data estructure store one item subcripcion (key) and subcriptors proxy list """
        # print("Im {} and {} -> {} (with pass:'{}') wants to susbscribe to me.".format(self.pyro4id, identifier, uri, mypassword))
        try:
            if identifier not in self.subscriptors:
                self.subscriptors[identifier] = []
            proxy = self.__dict__["uriresolver"].get_proxy(uri) if mypassword is None else self.__dict__[
                "uriresolver"].get_proxy(uri, passw=mypassword)
            self.subscriptors[identifier].append(proxy)
            return True
        except Exception:
            print("ERROR: in subscribe")
            return False


    @Pyro4.oneway
    @Pyro4.expose
    def publication(self, key, value):
        """ Is used to public in this object a item value """
        try:
            # print("setattr",key,value)
            setattr(self, key, value)
        except Exception:
            raise

    def adquire(self):
        self.mutex.adquire()

    def release(self):
        self.mutex.release()

    def stop(self):
        self.worker_run = False

    @Pyro4.expose
    def get_pyroid(self):
        return self.pyro4id

    @Pyro4.expose
    def __exposed__(self):
        return self.exposed

    @Pyro4.expose
    def __docstring__(self):
        return self.docstring

    @Pyro4.expose
    def get_class(self):
        return self._dict__[cls]

    @Pyro4.expose
    @Pyro4.callback
    def add_resolved_remote_dep(self, dep):
        # print(colored("New remote dep! {}".format(dep), "green"))
        if isinstance(dep, dict):
            k = dep.keys()[0]
            try:
                for u in dep[k]:
                    self.deps[k] = utils.get_pyro4proxy(u, k.split(".")[0])
                self._resolved_remote_deps.append(dep[k])
                if (self._unr_remote_deps is not None):
                    if k in self._unr_remote_deps:
                        self._unr_remote_deps.remove(k)
            except Exception:
                print("Error in control.add_resolved_remote_dep() ", dep)
            self.check_remote_deps()
        else:
            print("Error in control.add_resolved_remote_dep(): No dict", dep)

    def check_remote_deps(self):
        status = True
        if (self._unr_remote_deps is not None and self._unr_remote_deps):
            for unr in self._unr_remote_deps:
                if "*" not in unr:
                    status = False
        for k in self.deps.keys():
            try:
                if (self.deps[k]._pyroHandshake != "hello"):
                    status = False
            except Exception:
                print("Error connecting to dep. ", k)
                status = False

        if (status):
            self._REMOTE_STATUS = "OK"
            try:
                self.node.status_changed()
            except Exception as e:
                print "Error in control.check_remote_deps: "+str(e)

        return self._REMOTE_STATUS

    @Pyro4.expose
    def get_status(self):
        return self._REMOTE_STATUS
