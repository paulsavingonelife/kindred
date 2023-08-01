###############################################################################
# File:          test2.s                                                      # 
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


        li s0, 0xA000
        li t0, 0
loop:   bge t0, 8, end
        slli t2, t0, 2
        add t3, s0, t2
        lw t4, 0(t3)
        sub t4, x0, t4
        sw t4, 0(t3)
        addi t0, t0, 1
        jal x0, loop
end:    nop
