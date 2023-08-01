###############################################################################
# File:          kindredsim.py                                                # 
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

import assembly_loader
import registers_unit
import inst_buffer_unit
import load_store_unit
import pipeline_unit
import vcd_trace
import inst_trace
import printer

import argparse

import vcd.common

def main():

    printer.Printer.set_verbosity(printer.PrinterVerbosity.DEBUG)   # FULL OUTPUT
    parser = argparse.ArgumentParser(
            prog='kindredsim',
            description='Kindred RiscV Simulator'
        )
    parser.add_argument('-w', '--workload', required=True)
    parser.add_argument('-v', '--vcd_trace', required=True)
    parser.add_argument('-i', '--inst_trace', required=True)
    args = parser.parse_args()

    # Build simulator
    printer.Printer.info('SIMULATOR', 'Setting up KINDRED simulator...')

    inst_buffer = inst_buffer_unit.KindredInstructionBufferUnit('kindred.inst_buffer')
    registers = registers_unit.KindredRegistersUnit('kindred.registers')
    lsu = load_store_unit.KindredLoadStoreUnit('kindred.lsu')
    pipeline = pipeline_unit.KindredPipeline('kindred.pipeline',inst_buffer,registers,lsu)

    # Load workload
    assembly_loader.RiscVAssemblyLoader.load(args.workload,inst_buffer)
    inst_buffer.display()

    if inst_buffer.size() > 0:

        sim_run = True
        cycle = 0
        edge = 0

        # Setup Trace / Stats
        vcd_trace_store = vcd_trace.KindredVcdTrace(args.vcd_trace)
        clock_var = vcd_trace_store.register('kindren','clk',vcd.common.VarType.integer,2,0)
        stage1_inst_vcd = vcd_trace_store.register('kindred.stage1','inst',vcd.common.VarType.string,20)
        inst_trace_store = inst_trace.KindredInstructionTrace(args.inst_trace)

        # Simulation Loop
        while sim_run:
            edge = edge + 1
            cycle = cycle + 1

            printer.Printer.debug( 'SIMULATOR', '----------------------> Stepping simulator...' )
            printer.Printer.debug( 'SIMULATOR', '   Cycle [{0}]'.format(cycle) )
            printer.Printer.debug( 'SIMULATOR', '   Current PC [{0}]'.format(registers.get('x0').value) )

            ######################################################################################################################
            # NEGEDGE - LATCH values from previous stage, Pre-fetch
            ######################################################################################################################
            printer.Printer.info( 'SIMULATOR', ' [[ CLOCK@NEGEDGE cycle={0} ]]'.format(cycle) )
            vcd_trace_store.change(clock_var,edge,0)
            pipeline.negedge(cycle)

            ######################################################################################################################
            # UPDATE (POSEDGE) - LSU, Write-Back Store
            ######################################################################################################################
            printer.Printer.info( 'SIMULATOR', ' [[ CLOCK@POSEDGE cycle={0} ]]'.format(cycle) )
            edge = edge + 1
            vcd_trace_store.change(clock_var,edge,1)
            pipeline.posedge(cycle)

            ######################################################################################################################
            # Display Cycle Summary
            ######################################################################################################################
            pipeline.display()
            registers.display()


            ######################################################################################################################
            # Check for Termination
            ######################################################################################################################
            if pipeline.empty_pipe():
                break
            if cycle == 10000:
                break

        # SUMMARY
        printer.Printer.verbose( 'SIMULATOR', 'Simulation complete')
        printer.Printer.verbose( 'SIMULATOR', '  Total Cycles        : {}'.format(cycle) )
        printer.Printer.verbose( 'SIMULATOR', '  Total Retired Inst  : {}'.format(pipeline.num_retired_instructions) )
        printer.Printer.verbose( 'SIMULATOR', '  CPI                 : {}'.format(cycle/pipeline.num_retired_instructions) )

    else:
        printer.Printer.error( 'SIMULATOR', 'No instructions we loaded')

if __name__ == "__main__":
    main()

