###############################################################################
# File:          assembly_loader.py                                           # 
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

import inst_buffer_unit
import printer

import re
import os
import traceback


class RiscVAssemblyLoader:

    reg_offset_re = r'^(?P<offset>[-]{0,1}[\d]+){1}[\s]*\((?P<reg>\D[\w]+){1}\)$'
    compiled_reg_offset_re = re.compile(reg_offset_re)
    op_hex_re = r"^0x[0-9a-f]+$"
    op_dec_re = r"^[\d]+$"
    op_reg_re = r"^[txs]{1}[0-9]+$"

    @staticmethod
    def load(filename: str, buffer: inst_buffer_unit.KindredInstructionBufferUnit ):
        if os.path.exists(filename):
            try:
                with open(filename,'r') as assembly:
                    printer.Printer.info( 'LOADER', 'Loading assembly: [{0}]'.format(filename) )
                    content = assembly.readlines()
                    assemre = re.compile(r'^((?P<label>[\w_]+){0,1}:){0,1}[\s]*(?P<inst>[\w]+){1}[\s]*(?P<dst>[\w]+){0,1}[\s]*(,[\s]*(?P<op1>[\w()]+)*){0,1}[\s]*(,[\s]*(?P<op2>[\w]+){0,1})*$',re.IGNORECASE)
                    for line in content:
                        line = line.strip()
                        if len(line) > 0 and line[0] != '#':
                            # Parse line of assembly
                            printer.Printer.debug( 'LOADER', f'  Parsing line: [{line}]' )
                            m = None
                            try:
                                m = assemre.match(line)
                            except Exception as e:
                                printer.Printer.error( 'LOADER', 'Could not parse line [{0}] from [{1}]'.format(line,filename) )
                                traceback.print_exception(type(e),e,e.__traceback__)
                            else:
                                try:
                                    if m:
                                        i = inst_buffer_unit.KindredRiscVInstruction( line, m.groupdict()['label'], m.groupdict()['inst'], m.groupdict()['dst'], m.groupdict()['op1'], m.groupdict()['op2'] )
                                        buffer.append(i)
                                except Exception as e:
                                    printer.Printer.error( 'LOADER', 'Could not create RiscV instruction from [{0}]'.format(line) )
                                    traceback.print_exception(type(e),e,e.__traceback__)
            except:
                printer.Printer.error( 'LOADER', 'Workload file [{filename}] could not be opened for read'.format(filename=filename) )
        else:
            printer.Printer.error( 'LOADER', 'Workload file [{filename}] was not found'.format(filename=filename) )

    @staticmethod
    def is_op_register(op):
        if op == None or not isinstance(op,str) or len(op) == 0:
            return False
        if re.fullmatch(RiscVAssemblyLoader.op_reg_re,op,re.IGNORECASE) is not None:
            return True
        return op == 'pc'
    
    @staticmethod
    def is_op_immediate(op):
        return RiscVAssemblyLoader.is_op_dec(op) or RiscVAssemblyLoader.is_op_hex(op)
    
    @staticmethod
    def is_op_reg_offset(op):
        if op == None or not isinstance(op,str) or len(op) == 0:
            return False
        return re.fullmatch(RiscVAssemblyLoader.reg_offset_re,op,re.IGNORECASE) is not None
    
    @staticmethod
    def is_op_hex(op):
        if op == None or not isinstance(op,str) or len(op) == 0:
            return False
        return re.fullmatch(RiscVAssemblyLoader.op_hex_re,op,re.IGNORECASE) is not None
    
    @staticmethod
    def is_op_dec(op):
        if op == None or not isinstance(op,str) or len(op) == 0:
            return False
        return re.fullmatch(RiscVAssemblyLoader.op_dec_re,op,re.IGNORECASE) is not None
   
    @staticmethod
    def parse_op_as_reg_offset(op):
        if op == None or not isinstance(op,str) or len(op) == 0:
            return None
        try:
            m = RiscVAssemblyLoader.compiled_reg_offset_re.match(op)
            if m:
                # Return list
                return [ int(m.groupdict()['offset']), m.groupdict()['reg'] ]
        except Exception:
            pass
        return None
    