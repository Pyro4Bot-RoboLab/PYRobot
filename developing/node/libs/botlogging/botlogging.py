#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# ________in collaboration with cristian vazquez _________
from node.libs.botlogging.coloramadefs import *

level_DEBUG = 40
level_INFO = 30
level_WARNING = 20
level_ERROR = 10
level_CRITICAL = 0


class Logging(object):
    def __init__(self, handler="", tty_out="", tty_err="", level=50):
        print(handler)
        self.Logging_level = level
        if hasattr(self, "name"):
            self.handler = self.name
        else:
            self.handler = ""
        self.Logging_out = ""
        self.Logging_err = ""

    def Logging_reconfigure(self, out="", err="", handler="", level=50):
        self.Logging_level = level
        self.Logging_handler = handler
        self.Logging_out = out
        self.Logging_err = err

    def L_debug(self, men):
        if self.Logging_level >= level_WARNING:
            print(log_color("[[FG]Debug[SR]]:<" + self.handler + "> " + str(men)))

    def L_warning(self, men):
        if self.Logging_level >= level_WARNING:
            print(log_color("[[FY]Warning[SR]]:<" + self.handler + "> " + str(men)))

    def L_info(self, men):
        if self.Logging_level >= level_INFO:
            print(log_color("[[FC]Info[SR]]:<" + self.handler + "> " + str(men)))

    def L_error(self, men):
        if self.Logging_level >= level_INFO:
            print(log_color("[[FR]ERROR[SR]]:<" + self.handler + "> " + str(men)))

    def L_critical(self, men):
        if self.Logging_level >= level_INFO:
            print(log_color("[[FR]CRITICAL[SR]]:<" + self.handler + "> " + str(men)))

    def L_print(self, men, handler=True):
        if handler:
            print(log_color("[FG]<" + self.handler + "> [SR]" + str(men)))
        else:
            print(log_color(str(men)))
