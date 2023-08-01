###############################################################################
# File:          inst_buffer_unit.py                                          # 
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

import registers_unit
import assembly_loader
import printer

class KindredRiscVInstruction:

    def __init__(self,assembly,label,inst,dst,op1,op2):
        """ RiscV instruction storage and "decoding" """

        # Categorize instructions - typically you would have potentially auto-generated 
        # code for instruction deccode and execution handlers in functional simulators
        self.reg_write_back_instructions = [
            "add"
            , "addi"
            , "li"
            , "lw"
            , 'slli'
            , 'slri'
            , "sub"
        ]
        self.mem_store_instructions = [
            "sw"
        ]
        self.mem_load_instructions = [
            "lw"
        ]
        self.id = 0
        self.assembly = assembly.lower() if assembly != None else ''
        self.label = label.lower() if label != None else ''
        self.inst = inst.lower() if inst != None else ''
        self.dst = dst.lower() if dst != None else ''
        self.op1 = op1.lower() if op1 != None else ''
        self.op2 = op2.lower() if op2 != None else ''

        self.reg_write_back = self.inst in self.reg_write_back_instructions
        self.mem_store = self.inst in self.mem_store_instructions
        self.mem_load = self.inst in self.mem_load_instructions

        # Check if dst/src opserands are registers and could cause pipe stage stall for THIS instruction
        # reg WB stall would be used for subsequent instruction stall conditions
        #
        # Register Read is only available in Fetch Stage
        # Register Write is only available in WB stage
        # Memory is only availale in Exec stage
        self.stall_regs = []
        if not self.reg_write_back and assembly_loader.RiscVAssemblyLoader.is_op_register(self.dst):
            self.stall_regs.append(self.dst)
        if assembly_loader.RiscVAssemblyLoader.is_op_register(self.op1):
            self.stall_regs.append(self.op1)
        elif assembly_loader.RiscVAssemblyLoader.is_op_reg_offset(self.op1):
            self.stall_regs.append(assembly_loader.RiscVAssemblyLoader.parse_op_as_reg_offset(self.op1)[1])
        if assembly_loader.RiscVAssemblyLoader.is_op_register(self.op2):
            self.stall_regs.append(self.op2)
        elif assembly_loader.RiscVAssemblyLoader.is_op_reg_offset(self.op2):
            self.stall_regs.append(assembly_loader.RiscVAssemblyLoader.parse_op_as_reg_offset(self.op2)[1])

    def has_reg_write_back(self):
        return self.reg_write_back

    def __str__(self):
        if self.label:
            return '{0}:   {1}, {2}, {3}, {4}'.format(self.label,self.inst,self.dst,self.op1,self.op2)
        return '       {1}, {2}, {3}, {4}'.format(self.label,self.inst,self.dst,self.op1,self.op2)


class KindredInstructionBufferUnit:
    """ Instruction Buffer Unit """
    def __init__(self,instance_name):
        self.instance_name = instance_name
        self.instructions = []
        self.labels = {}

    def append(self, instruction : KindredRiscVInstruction):
        if len(instruction.inst) > 0:
            instruction.id = len(self.instructions)+1
            self.instructions.append(instruction)
        if len(instruction.label) > 0:
            self.labels[instruction.label] = len(self.instructions)-1
            printer.Printer.info( 'INSTBUFFER', 'Label [{0}] set at address [{1}]'.format(instruction.label,self.labels[instruction.label]) )

    def fetch(self,addr) -> KindredRiscVInstruction:
        if self.has_instruction_at(addr):
            return self.instructions[addr]
        return None
    
    def label_addr(self,label):
        if label.lower() in self.labels:
            return self.labels[label.lower()]
        return None
    
    def size(self):
        return len(self.instructions)
    
    def has_instruction_at(self,addr):
        """ Fetch have instructions to execute? """
        return addr < len(self.instructions)

    def display(self):
        printer.Printer.info( 'INSTBUFFER', '-----------------------------------------------------------------------------------' )
        printer.Printer.info( 'INSTBUFFER', '                                ASSEMBLY' )
        printer.Printer.info( 'INSTBUFFER', '-----------------------------------------------------------------------------------' )
        for inst in self.instructions:
            printer.Printer.info( 'INSTBUFFER', '{0}'.format(inst.assembly) )
        printer.Printer.info( 'INSTBUFFER', '-----------------------------------------------------------------------------------' )
    


class KindredRiscVInstructionDecode:
    """ Simpel representation of a decoded instruction """
    def __init__(self,inst : KindredRiscVInstruction):
        self.instruction = inst
        self.dst_value = None
        self.op1_value = None
        self.op2_value = None
        self.lsu_value = None
        self.resultant = None

        # Runtime settings
        self.reserved_regs = []
        self.stalled = False

    def reset(self):
        self.reserved_regs = []
        self.resultant = 0
        self.lsu_value = 0

    def reserve_regs(self,regs):
        if isinstance(regs,list):
            self.reserved_regs = regs

    def fetch_op_values(self, registers: registers_unit.KindredRegistersUnit, inst_buffer: KindredInstructionBufferUnit):
        self.dst_value = 0
        if self.instruction.mem_load:
            self.dst_value = self.fetch_op_value(self.instruction.dst,registers,inst_buffer)
        self.op1_value = self.fetch_op_value(self.instruction.op1,registers,inst_buffer)
        self.op2_value = self.fetch_op_value(self.instruction.op2,registers,inst_buffer)

    def fetch_op_value(self, op : str, registers: registers_unit.KindredRegistersUnit, inst_buffer: KindredInstructionBufferUnit):
        if op != None:
            if assembly_loader.RiscVAssemblyLoader.is_op_register(op):
                return registers.read(op)
            elif assembly_loader.RiscVAssemblyLoader.is_op_reg_offset(op):
                params = assembly_loader.RiscVAssemblyLoader.parse_op_as_reg_offset(op)
                return registers.read(params[1]) + params[0]
            elif assembly_loader.RiscVAssemblyLoader.is_op_hex(op):
                return int(op,16)
            elif assembly_loader.RiscVAssemblyLoader.is_op_dec(op):
                return int(op)
            else:
                return inst_buffer.label_addr(op)
        return None

