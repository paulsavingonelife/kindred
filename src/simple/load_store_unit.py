###############################################################################
# File:          load_store_unit.py                                           # 
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

class KindredLoadStoreUnit:
    """ Super-duper simple LSU """

    def __init__(self,instance_name):
        self.instance_name = instance_name
        self.memory = {}

    def write(self, addr, value):
        self.memory[addr] = value

    def read(self, addr):
        if addr in self.memory:
            return self.memory[addr]
        return 0
