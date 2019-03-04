#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
from libs.class_client_robot import ClientRobot
import time
import Pyro4


def show_component_methods(bot):
    for var in vars(bot):
        print("component:", var, ", with methods:")
        eval("[print(bot.{}.__docstring__()) if type(bot.{}) == Pyro4.core.Proxy else None]"
             .format(var, var))


def main():
    bot = ClientRobot("<robot>")


if __name__ == '__main__':
    main()
