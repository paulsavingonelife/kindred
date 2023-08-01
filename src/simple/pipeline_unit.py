###############################################################################
# File:          pipeline_unit.py                                             # 
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

class KindredPipeline:

    def __init__(self,instance_name,inst_buffer,registers,lsu):
        self.instance_name = instance_name
        self.inst_buffer = inst_buffer
        self.registers = registers
        self.lsu = lsu

        # PIPE (Latch decoded instructions)       
        self.stage1_fetch_input_latch : inst_buffer_unit.KindredRiscVInstructionDecode = None
        self.stage1_fetch_output_latch : inst_buffer_unit.KindredRiscVInstructionDecode = None
        self.stage2_exec_input_latch : inst_buffer_unit.KindredRiscVInstructionDecode = None
        self.stage2_exec_output_latch : inst_buffer_unit.KindredRiscVInstructionDecode = None
        self.stage3_wb_input_latch : inst_buffer_unit.KindredRiscVInstructionDecode = None
        self.stage3_wb_output_latch : inst_buffer_unit.KindredRiscVInstructionDecode = None

        self.exec_lsu_delay : int = 0
        self.load_store_unit_access_delay : int = 1

        self.num_retired_instructions = 0

    def negedge(self,cycle):
        # WB NegEdge
        if self.stage3_wb_input_latch == None:
            # STAGE3: Latch EXEC instruction
            # Stage is open for processing (latch input)
            # Access to instruction operands and registers
            if self.exec_lsu_delay == 0:
                self.stage3_wb_output_latch = None
                if self.stage2_exec_output_latch != None:
                    # Pull from STAGE2
                    printer.Printer.debug( 'STAGE3', f'Latch decoded instruction from STAGE2' )
                    self.stage3_wb_input_latch = self.stage2_exec_output_latch
                    self.stage2_exec_output_latch = None

        # EXEC NegEdge
        if self.stage2_exec_input_latch == None:
            # STAGE2: Latch FETCH instruction
            # Stage is open for processing (latch input)
            # Access to instruction, operand values and memory via LSU            
            if self.stage1_fetch_output_latch != None:
                # Pull from STAGE1
                printer.Printer.debug( 'STAGE2', f'Latch decoded instruction from STAGE1 [{self.stage1_fetch_output_latch.instruction.inst}]' )
                self.stage2_exec_input_latch = self.stage1_fetch_output_latch
                self.stage1_fetch_output_latch = None
        
        # FETCH NegEdge
        if self.stage1_fetch_input_latch == None:
            # STAGE1: Fetch next instruction if possible
            # Stage is open for processing (latch input)
            # Access to instruction and registers and literals
            pc = self.registers.get('pc')
            printer.Printer.debug( 'STAGE1', f'Pre-fetch next instruction @PC={pc.value}...' )
            next_inst = self.inst_buffer.fetch(pc.value)
            reserved_regs = []
            if next_inst != None:
                # Check to see if we should stall
                #   - Any src op registers are currently scheduled for WB
                #           OR
                #   - Reg write-back is scheduled for WB
                if not self.registers.is_reserved('pc') and not ( next_inst.has_reg_write_back() and self.registers.is_reserved(next_inst.dst) ) and ( not self.registers.is_reserved(next_inst.stall_regs) ):
                    # vcd_trace_store.change(stage1_inst_vcd,edge,next_inst.inst)
                    # No stall condition
                    # 'pc' stall is for jumps or conditional branches that have triggered
                    printer.Printer.debug( 'STAGE1', 'No Stall. Fetching next instruction...' )
                    # Some instruction behavior necessary for model
                    if next_inst.inst == 'jal':
                        # JUMP
                        printer.Printer.debug( 'STAGE1', 'JAL jump' )
                        reserved_regs = [next_inst.dst,'pc']
                    elif next_inst.inst == 'bge':
                        # COnditional Branch
                        rval = self.registers.read(next_inst.dst)
                        if rval >= int(next_inst.op1):
                            ## BRANCH TO LOOP
                            printer.Printer.debug( 'STAGE1', 'BGE branch condition met' )
                            reserved_regs = [next_inst.dst,'pc']
                        else:
                            # NO Branch
                            self.registers.increment('pc',1)
                    elif next_inst.inst == 'ble':
                        # COnditional Branch
                        rval = self.registers.read(next_inst.dst)
                        if rval <= int(next_inst.op1):
                            ## BRANCH TO LOOP
                            printer.Printer.debug( 'STAGE1', 'BLE branch condition met' )
                            reserved_regs = [next_inst.dst,'pc']
                        else:
                            # NO Branch
                            self.registers.increment('pc',1)
                    elif next_inst.inst == 'lw':
                        reserved_regs = [next_inst.dst]
                        self.registers.increment('pc',1)
                    elif next_inst.reg_write_back:
                        # Instruction with store to a register
                        reserved_regs = [next_inst.dst]
                        self.registers.increment('pc',1)
                    else:
                        # All other instructions
                        self.registers.increment('pc',1)

                    # Decoded Instruction
                    self.stage1_fetch_input_latch = inst_buffer_unit.KindredRiscVInstructionDecode(next_inst)
                    self.stage1_fetch_input_latch.reserve_regs(reserved_regs)
                    self.registers.reserve(reserved_regs)
                else:
                    # Write-back hazard, stall
                    printer.Printer.verbose( 'STAGE1', 'STALL - Write-back hazard' )
            else:
                # No instruction @PC - wait for pipe to complete
                pass

    def posedge(self,cycle):
        # WB PosEdge
        if self.stage3_wb_input_latch != None:
            # Calculate results and store in register if necessary
            if self.stage3_wb_input_latch.instruction.inst == 'jal':
                if self.stage3_wb_input_latch.instruction.dst in self.stage3_wb_input_latch.reserved_regs:
                    laddr = self.stage3_wb_input_latch.op1_value
                    printer.Printer.debug( 'STAGE3', 'Performing JAL instruction - Jump to address={0}'.format(laddr) )
                    self.registers.write_back(self.stage3_wb_input_latch.instruction.dst,laddr)
                    self.registers.write_back('pc',laddr)
                    self.registers.release(self.stage3_wb_input_latch.reserved_regs)
            elif self.stage3_wb_input_latch.instruction.inst == 'bge':
                if self.stage3_wb_input_latch.instruction.dst in self.stage3_wb_input_latch.reserved_regs:
                    laddr = self.inst_buffer.label_addr(self.stage3_wb_input_latch.instruction.op2)
                    printer.Printer.debug( 'STAGE3', 'Performing BGE instruction - Jump to address={0}, label={1}'.format(laddr,self.stage3_wb_input_latch.instruction.op2) )
                    self.registers.write_back(self.stage3_wb_input_latch.instruction.op1,laddr)
                    self.registers.write_back('pc',laddr)
                    self.registers.release(self.stage3_wb_input_latch.reserved_regs)
            elif self.stage3_wb_input_latch.instruction.inst == 'ble':
                if self.stage3_wb_input_latch.instruction.dst in self.stage3_wb_input_latch.reserved_regs:
                    laddr = self.inst_buffer.label_addr(self.stage3_wb_input_latch.instruction.op2)
                    printer.Printer.debug( 'STAGE3', 'Performing BLE instruction - Jump to address={0}, label={1}'.format(laddr,self.stage3_wb_input_latch.instruction.op2) )
                    self.registers.write_back(self.stage3_wb_input_latch.instruction.op1,laddr)
                    self.registers.write_back('pc',laddr)
                    self.registers.release(self.stage3_wb_input_latch.reserved_regs)
            elif self.stage3_wb_input_latch.instruction.reg_write_back:
                printer.Printer.debug( 'STAGE3', 'Performing register write-back [{0}=>{1}]'.format(self.stage3_wb_input_latch.resultant,self.stage3_wb_input_latch.instruction.dst) )
                self.registers.write_back(self.stage3_wb_input_latch.instruction.dst,self.stage3_wb_input_latch.resultant)
                self.registers.release(self.stage3_wb_input_latch.reserved_regs)
            printer.Printer.info( 'STAGE3', 'Retiring instruction [{0}]'.format(self.stage3_wb_input_latch.instruction.assembly) )
            printer.Printer.verbose('STAGE3',f'CYCLE={cycle:5} - {self.stage3_wb_input_latch.instruction.assembly}' )
            # t1 = self.registers.read('t1')
            # printer.Printer.verbose( 'REGISTERS','ti = {0}'.format(hex(t1)) )
            # inst_trace_store.retire(cycle,self.stage3_wb_input_latch.instruction.assembly)
            self.stage3_wb_output_latch = self.stage3_wb_input_latch
            self.stage3_wb_input_latch.reset()
            self.stage3_wb_input_latch = None
            self.num_retired_instructions = self.num_retired_instructions + 1

        # EXEC PosEdge
        if self.stage2_exec_input_latch != None:
            # Processing an LSU access as well as performing ALU ops
            complete_stage = False
            if self.exec_lsu_delay > 0:
                self.exec_lsu_delay = self.exec_lsu_delay - 1
                complete_stage = self.exec_lsu_delay == 0

            if self.stage2_exec_input_latch.instruction.mem_store:
                if self.stage2_exec_input_latch.instruction.inst == 'sw':
                    if complete_stage:
                        # Store value
                        self.lsu.write(self.stage2_exec_input_latch.op1_value,self.stage2_exec_input_latch.dst_value)
                        printer.Printer.debug( 'STAGE2', 'STORE request to LSU completed [addr={0}]'.format(hex(self.stage2_exec_input_latch.op1_value)) )
                        self.stage2_exec_input_latch.lsu_value = self.stage2_exec_input_latch.dst_value
                    else:
                        # Stall
                        printer.Printer.debug( 'STAGE2', 'Sending STORE request to LSU [addr={0},value={1}]'.format(hex(self.stage2_exec_input_latch.op1_value),hex(self.stage2_exec_input_latch.dst_value)) )
                        self.exec_lsu_delay = self.load_store_unit_access_delay
            elif self.stage2_exec_input_latch.instruction.mem_load:
                if self.stage2_exec_input_latch.instruction.inst == 'lw':
                    if complete_stage:
                        # Load value
                        v = self.lsu.read(self.stage2_exec_input_latch.op1_value)
                        printer.Printer.debug( 'STAGE2', 'LOAD request to LSU completed [addr={0},value={1}]'.format(hex(self.stage2_exec_input_latch.op1_value),hex(v)) )
                        self.stage2_exec_input_latch.lsu_value = v
                    else:
                        # Stall
                        printer.Printer.debug( 'STAGE2', 'Sending LOAD request to LSU [addr={0}]'.format(hex(self.stage2_exec_input_latch.op1_value)) )
                        self.exec_lsu_delay = self.load_store_unit_access_delay
            else:
                # Any other instruction
                complete_stage = True
            if complete_stage and self.stage2_exec_input_latch.instruction.reg_write_back:
                self.stage2_exec_input_latch.resultant = 0
                if self.stage2_exec_input_latch.instruction.inst == 'li':
                    # dst = op1
                    self.stage2_exec_input_latch.resultant = self.stage2_exec_input_latch.op1_value
                elif self.stage2_exec_input_latch.instruction.inst == 'addi':
                    # dst = op1 + imm
                    self.stage2_exec_input_latch.resultant = self.stage2_exec_input_latch.op1_value + self.stage2_exec_input_latch.op2_value
                elif self.stage2_exec_input_latch.instruction.inst == 'add':
                    # dst = op1 + op2
                    self.stage2_exec_input_latch.resultant = self.stage2_exec_input_latch.op1_value + self.stage2_exec_input_latch.op2_value
                elif self.stage2_exec_input_latch.instruction.inst == 'slli':
                    # shift-left im (NOT NEEDED)
                    self.stage2_exec_input_latch.resultant = self.stage2_exec_input_latch.op1_value << self.stage2_exec_input_latch.op2_value
                    pass
                elif self.stage2_exec_input_latch.instruction.inst == 'slri':
                    # shift-right im (NOT NEEDED)
                    self.stage2_exec_input_latch.resultant = self.stage2_exec_input_latch.op1_value >> self.stage2_exec_input_latch.op2_value
                elif self.stage2_exec_input_latch.instruction.inst == 'sub':
                    # dst = op1 - op2
                    self.stage2_exec_input_latch.resultant = self.stage2_exec_input_latch.op1_value - self.stage2_exec_input_latch.op2_value
                printer.Printer.debug( 'STAGE2', 'Resultant calculated [{0} :: resultant={1}]'.format(self.stage2_exec_input_latch.instruction.assembly,self.stage2_exec_input_latch.resultant) )

            # Latch decoded instruction in output latch
            #   Latch after memory access
            if complete_stage:
                printer.Printer.debug( 'STAGE2', 'Complete EXEC stage' )
                self.stage2_exec_output_latch = self.stage2_exec_input_latch
                self.stage2_exec_input_latch = None
            else:
                printer.Printer.verbose( 'STAGE2', 'STALL pipeline for LSU response [addr={0}]'.format(hex(self.stage2_exec_input_latch.op1_value)) )
                self.stage2_exec_output_latch = self.stage2_exec_input_latch
                # self.stage2_exec_input_latch = None

        # FETCH PosEdge
        if self.stage1_fetch_input_latch != None and self.stage1_fetch_output_latch == None:
            # Latch operaand values
            self.stage1_fetch_input_latch.fetch_op_values(self.registers,self.inst_buffer)
            # Latch decoded instruction in output latch
            self.stage1_fetch_output_latch = self.stage1_fetch_input_latch
            self.stage1_fetch_input_latch = None

    def empty_pipe(self):
        pc = self.registers.read('pc')
        return pc >= self.inst_buffer.size() and (self.stage1_fetch_output_latch == None and self.stage2_exec_output_latch == None)

    def display(self):
        printer.Printer.info( 'SIMULATOR', '----------------------------------------------------------------------------------' )
        printer.Printer.info( 'SIMULATOR', '                                PIPELINE' )
        printer.Printer.info( 'SIMULATOR', '----------------------------------------------------------------------------------' )
        pipe_hdr = '|  {0:22}  |  {1:22}  |  {2:22}  |'.format('FETCH','EXEC','WB')
        printer.Printer.info( 'SIMULATOR', pipe_hdr )
        printer.Printer.info( 'SIMULATOR', '----------------------------------------------------------------------------------' )
        stage1_msg = '{0}'.format(self.stage1_fetch_output_latch.instruction.inst) if self.stage1_fetch_output_latch != None else 'X'
        stage2_msg = '{0}'.format(self.stage2_exec_output_latch.instruction.inst) if self.stage2_exec_output_latch != None else 'X'
        stage3_msg = '{0}'.format(self.stage3_wb_output_latch.instruction.inst) if self.stage3_wb_output_latch != None else 'X'
        pipe = f'|  {stage1_msg:22}  |  {stage2_msg:22}  |  {stage3_msg:22}  |'
        printer.Printer.info( 'SIMULATOR', pipe )
        printer.Printer.info( 'SIMULATOR', '----------------------------------------------------------------------------------' )
        stage1_msg = '[STAGE1] inst=[{0}]'.format(self.stage1_fetch_output_latch.instruction.assembly) if self.stage1_fetch_output_latch != None else '[STAGE1] inst=[X]'
        stage2_msg = '[STAGE2] inst=[{0}]'.format(self.stage2_exec_output_latch.instruction.assembly) if self.stage2_exec_output_latch != None else '[STAGE2] inst=[X]'
        stage3_msg = '[STAGE3] inst=[{0}]'.format(self.stage3_wb_output_latch.instruction.assembly) if self.stage3_wb_output_latch != None else '[STAGE3] inst=[X]'
        printer.Printer.info( 'SIMULATOR', stage1_msg )
        printer.Printer.info( 'SIMULATOR', stage2_msg )
        printer.Printer.info( 'SIMULATOR', stage3_msg )
        printer.Printer.info( 'SIMULATOR', '----------------------------------------------------------------------------------' )
