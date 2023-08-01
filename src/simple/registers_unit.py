###############################################################################
# File:          registers_unit.py                                            # 
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

import printer

import abc

class KindredRegister:
    
    def __init__(self):
        self.value = 0

class KindredRegistersInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def reserve(self,name):
        """ Reserve a register for RAW hazard (pipe stall)"""
        pass

    @abc.abstractmethod
    def release(self,name):
        """ Release a register from RAW hazard (pipe stall)"""
        pass

    @abc.abstractmethod
    def get(self,name) -> KindredRegister:
        """ Release a register from RAW hazard (pipe stall)"""
        pass

class KindredRegistersUnit(KindredRegistersInterface):
    
    def __init__(self,instance_name):
        self.instance_name = instance_name
        self.registers = {
            'pc' : KindredRegister()
            , 'x0' : KindredRegister()
            , 'x1' : KindredRegister()
            , 'x2' : KindredRegister()
            , 'x3' : KindredRegister()
            , 'x4' : KindredRegister()
            , 'x5' : KindredRegister()
            , 't0' : KindredRegister()
            , 't1' : KindredRegister()
            , 't2' : KindredRegister()
            , 't3' : KindredRegister()
            , 't4' : KindredRegister()
            , 't5' : KindredRegister()
            , 's0' : KindredRegister()
            , 's1' : KindredRegister()
            , 's2' : KindredRegister()
            , 's3' : KindredRegister()
            , 's4' : KindredRegister()
            , 's5' : KindredRegister()
        }
        self.reserved_registers = {}

    def is_reserved(self,regs):
        if isinstance(regs,str):
            lname = regs.lower()
            return lname in self.reserved_registers
        elif isinstance(regs,list):
            for reg in regs:
                if self.is_reserved(reg):
                    return True
        return False

    def reserve(self,regs):
        if isinstance(regs,str):
            lname = regs.lower()
            if not lname in self.reserved_registers:
                r = self.get(lname)
                if r:
                    printer.Printer.debug( 'REGISTERS', 'Reserving register [{0}] for stage3 write-back'.format(lname) )
                    self.reserved_registers[lname] = r
            else:
                printer.Printer.debug( 'REGISTERS', 'Register [{0}] already reserved for stage3 writeback'.format(lname) )
        elif isinstance(regs,list):
            for reg in regs:
                self.reserve(reg)
    
    def release(self,regs):
        if isinstance(regs,str):
            lname = regs.lower()
            if lname in self.reserved_registers:
                printer.Printer.info( 'REGISTERS', 'Releasing register [{0}]'.format(lname) )
                self.reserved_registers.pop(lname)
        elif isinstance(regs,list):
            for reg in regs:
                self.release(reg)
                
    def get(self,name) -> KindredRegister:
        lname = name.lower()
        if lname in self.registers:
            r = self.registers[lname]
            return r
        printer.Printer.error( 'REGISTERS', 'Invalid register [{0}]'.format(name) )
        return None
    
    def read(self,name) -> KindredRegister:
        lname = name.lower()
        if lname in self.registers:
            r = self.registers[lname]
            return int(r.value)
        printer.Printer.error( 'REGISTERS', 'Invalid register [{0}]'.format(name) )
        return None
    
    def write_back(self,name,value):
        lname = name.lower()
        if lname in self.registers:
            v = value
            if isinstance(value,str):
                v = int(value,0)
            self.registers[lname].value = v
    
    def increment(self,name,increment):
        lname = name.lower()
        if lname in self.registers:
            v = increment
            if isinstance(increment,str):
                v = int(increment)
            self.registers[lname].value = self.registers[lname].value + v

    def display(self):
        printer.Printer.info( 'REGISTERS', '----------------------------------------------------------------------------------' )
        printer.Printer.info( 'REGISTERS', '                                REGISTER VALUES' )
        printer.Printer.info( 'REGISTERS', '----------------------------------------------------------------------------------' )
        for name,reg in self.registers.items():
            stall = ' :: WB STALL' if self.is_reserved(name) else ''
            printer.Printer.info( 'REGISTERS', '{0} = {1}{2}'.format(name.upper(), hex(reg.value), stall) )
        printer.Printer.info( 'REGISTERS', '----------------------------------------------------------------------------------' )
