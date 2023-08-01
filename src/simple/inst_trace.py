###############################################################################
# File:          inst_trace.py                                                # 
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

class KindredInstructionTrace:
    
    def __init__(self,filename):
        self.filename = filename
        self.file = None
        self.open(filename)

    def __del__(self):
        if self.file:
            self.file.close()

    def open(self,filename):
        self.file = open(self.filename,"w")

    def retire(self,cycle,assembly):
        if self.file:
            self.file.write( f'CYCLE={cycle:5} :: {assembly}\n' )
