###############################################################################
# File:          test3.s                                                      # 
# Project:       Kindred                                                      # 
# Author:        Paul Klein                                                   # 
# EMail:         pauljkaz@gmail.com                                           # 
# -----                                                                       # 
# Last Modified: Sun Jul 30 2023                                              # 
# Modified By:   Paul Klein                                                   # 
# -----                                                                       # 
#                                                                             # 
#  Copyright (c) 2019 - 2023 N/A, All Rights Reserved.                        # 
#                                                                             # 
###############################################################################


                li s0, 0xA000
                li t0, 0
outer_loop:     bge t0, 3, end
                li t1, 0
inner_loop:     slri t2, t0, 2
                add t3, s0, t2
                lw t4, 0(t3)
                addi t4, t4, 100
                sw t4, 0(t3)
                addi t1, t1, 1
                ble t1, 9, inner_loop
                addi t0, t0, 1
                jal x0, outer_loop
end:            nop
