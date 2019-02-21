#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
# All data defined in json configuration are attributes in your code object
from node.libs import control
import Pyro4


class <ClassName>(control.Control):
    __REQUIRED = []

    def __init__(self):
        # Atribute example
        self.value = 0

        # Worker starting example
        self.start_worker(self.worker)

    def worker(self):
        while self.worker_run:
            # write here code for your component thread
            pass

    #  here your methods
    #  Expose your method to exterior with decorator @Pyro4.expose
    @Pyro4.expose
    def get_value(self):
        return self.value

   
