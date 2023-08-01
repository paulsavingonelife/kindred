# Overview

Kindred super awesome 3-stage processor. Detailed pipe and register information is printed on the console during simulation. Additionally, 
an instruction trace is create and placed in a file <test>.inst. I started to add VCD support, but it has been a looooong time since I did 
anything with VCD. So that was not completed.

## Design

I chose to write this simulator in Python primarily for the fun. I started writing my own simple set of ports, etc. but backed out of that because #1 
this simulator is not that complicated and #2 it was taking too long to build the framework. I looked at PyMTL as well, but that seemed like overkill
as well. I had hoped this would be cleaner and simpler, but I wanted to demonstrate some u-arch understanding as well as take a sort of execution based
model approach. Ideally I would have had evaluate/update on each clock, but I just show a posedge/negedge instead.

Source code is in the src/ folder. Workloads are in RISV syntax in workloads/ folder.

## Dependencies

I used python v3.11 on Windows.

```
prompt> pip install pyvcd
```

## Running the Simulator

Use the run.bat to simplify running Kindred. It is setup to run with maximum verbose output.

```
prompt> run.bat test1
prompt> run.bat test2
prompt> run.bat test3
```

# Results

## TEST1

```
[VERBOSE] [SIMULATOR ] - Simulation complete
[VERBOSE] [SIMULATOR ] -   Total Cycles        : 14
[VERBOSE] [SIMULATOR ] -   Total Retired Inst  : 6
[VERBOSE] [SIMULATOR ] -   CPI                 : 2.3333333333333335
```

## TEST2

```
[VERBOSE] [SIMULATOR ] - Simulation complete
[VERBOSE] [SIMULATOR ] -   Total Cycles        : 170
[VERBOSE] [SIMULATOR ] -   Total Retired Inst  : 68
[VERBOSE] [SIMULATOR ] -   CPI                 : 2.5
```

## TEST3

Pretty hefty CPI! We need to work on our register dependent stalls and build a better compiler that doesn't re-use registers in back to back instructions.
Or consider adding a host of other HW elements (register renaming, branch prediction, out of order, etc) to improve our performance.

```
[VERBOSE] [SIMULATOR ] - Simulation complete
[VERBOSE] [SIMULATOR ] -   Total Cycles        : 652
[VERBOSE] [SIMULATOR ] -   Total Retired Inst  : 226
[VERBOSE] [SIMULATOR ] -   CPI                 : 2.8849557522123894
```