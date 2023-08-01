###############################################################################
# File:          test1.s                                                      # 
# Project:       Kindred                                                      # 
# Author:        Paul Klein                                                   # 
# EMail:         pauljkaz@gmail.com                                           # 
# -----                                                                       # 
# Last Modified: Sat Jul 29 2023                                              # 
# Modified By:   Paul Klein                                                   # 
# -----                                                                       # 
#                                                                             # 
#  Copyright (c) 2019 - 2023 N/A, All Rights Reserved.                        # 
#                                                                             # 
###############################################################################


synth_a:    li t0, 0
loop:       bge t0, 1, end
            addi t0, t0, 1
            jal x0, loop
end:        nop