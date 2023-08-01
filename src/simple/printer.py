###############################################################################
# File:          printer.py                                                   # 
# Project:       Kindred                                                      # 
# Author:        Paul Klein                                                   # 
# EMail:         pauljkaz@gmail.com                                           # 
# -----                                                                       # 
# Last Modified: Mon Jul 31 2023                                              # 
# Modified By:   Paul Klein                                                   # 
# -----                                                                       # 
#                                                                             # 
#  Copyright (c) 2019 - 2023 N/A, All Rights Reserved.                        # 
#                                                                             # 
###############################################################################

from enum import Enum

class PrinterVerbosity(Enum):
    NONE = 1
    INFO = 2
    WARN = 3
    DEBUG = 4
    ALL = 10

class Printer:

    verbosity = PrinterVerbosity.NONE

    @staticmethod
    def set_verbosity(v):
        Printer.verbosity = v

    @staticmethod
    def info(scope,msg):
        if Printer.verbosity.value >= int(PrinterVerbosity.INFO.value):
            Printer._print('INFO',scope,msg)

    @staticmethod
    def warn(scope,msg):
        if Printer.verbosity.value >= int(PrinterVerbosity.WARN.value):
            Printer._print('WARN',scope,msg)

    @staticmethod
    def debug(scope,msg):
        if Printer.verbosity.value >= int(PrinterVerbosity.DEBUG.value):
            Printer._print('DEBUG',scope,msg)

    @staticmethod
    def error(scope,msg):
        Printer._print('ERROR',scope,msg)

    @staticmethod
    def _print(type,scope,msg):
        print( f'[{type:6}] [{scope:10}] - {msg}' )

    @staticmethod
    def verbose(scope,msg):
        Printer._print('VERBOSE',scope,msg)
