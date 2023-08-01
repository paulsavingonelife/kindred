###############################################################################
# File:          vcd_trace.py                                                 # 
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

from vcd import VCDWriter

class KindredVcdTrace:
    
    def __init__(self,filename):
        self.filename = filename
        self.file = None
        self.vcdwriter = None
        self.open(filename)

    def __del__(self):
        if self.file:
            self.file.close()

    def open(self,filename):
        self.file = open(self.filename,"w")
        if self.file:
            self.vcdwriter = VCDWriter(self.file, timescale='1 ns', date='today')

    def register(self,scope,name,var_type,size,init='x'):
        if self.vcdwriter:
            return self.vcdwriter.register_var(scope,name,var_type,size,init)
        
    def change(self,var,timestamp,value):
        if self.vcdwriter:
            self.vcdwriter.change(var,timestamp,value)
