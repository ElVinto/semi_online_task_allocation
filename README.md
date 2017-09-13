# Semi Online Task Allocation Simulator

This document describes the different input parameters and output files of the semi-online simulator.

## Setup

This tool required python 2.7 and cplex v 12.6 or higher.

## Command Line
```
`cd src/onlineSolving/`
then
`python onlineSolver.py`
or 
`python onlineSolver.py  heu err timeStep ordering`
```

- `heu` is label denoting an solving heuristic adapted to the semi-online context. The list of possible heuristic label is presented in  next section "Adapted Bin Packing Heuristics". The default heuristic is FMF (First Merge Fit).

- `err` is an integer denoting the uncertainty on each task duration. Let d be the duration of a task, when the error is x, the expected duration utilised by heuristics is a random interger drawn from the segment [max(d*(1-x%), 0),d*(1+x%)] uniformly. The possible input errors in [0, 50, 100, 150, 200, 250, 350, 400]. The default error is set to 0.

- `timeStep` is a non negative integer denoting the size of each time step in seconds. The default timeStep is set to 0.

- `ordering` is a label representing the task ordering. The default task ordering is DDUR (Decreasing Duration), the different options are listed in the section "Ordering".

## Adapted bin Packing Heuristics
- `myFF`: First Fit
- `myBFD`: Best Fit on Duration
- `myBFR`: Best Fit on Requirement
- `myNF`: Next Fit 
- `myMRR`: Max Rest on Requirement
- `myMRD`: Max Rest on Duration
- `mySS`: Sum Square
- `myHA`: Harmonic

All the above heuristics can be ran as the input of a RNIS local search algorithm implemented in  CPLEX. For this purpose, the heuristic label has to be followed by `_CPLEX`. Consequently, the following heuristic strategies are also available: `FMF_CPLEX`, `myFF_CPLEX`, `myBFD_CPLEX`, `myBFR_CPLEX`, `myNF_CPLEX`, `myMRR_CPLEX`,`myMRD_CPLEX`, `mySS_CPLEX`, `myHA_CPLEX`.

## Ordering of tasks within the time step
- `LIST` ordered by arrival time increasing
- `RAND` randomly ordered
- `DREQ` decreasing cpu requirement
- `DDUR` decreasing duration
- `DDTR` decreasing by value (duration * requirement)

## Input file
When launching the command line `python onlineSolver.py heu err timeStep ordering`, the simulator will read the instance file "./src/data/allTasks_U`err`.csv". Each line of this file specifies the characteristics of an incoming task. The columns represents for each task: the arrival time stamp (in nano seconds), the task Id, the cpu requirement (percentage), the ram requirement (percentage), the actual duration (in seconds), the expected duration (in seconds).

## Output files

When launching the command line `python onlineSolver.py heu err timeStep ordering`, the simulator creates four output files  in the folder "./results/uncertain/", all terminating by `_alltasks_Uerr_heu_ordering_timeStep.csv`.
- File `usage` records a line per time step. The column respectively denote [time stamp of the start of time step in nanoseconds], [time stamp of the end of the time step in nanoseconds], [number of machines hosting at least a task during the current time step], [number of machines hosting at least a task during the current time step * size of time step in seconds]

- File `res` records a line per assignement. The columns respectively denote [the task Id], [the machine Id], [time stamp of the arrival time of the task in nanoseconds], [time stamp of the time step in which the task will start in nanoseconds], [time stamp of the finishing time of the task in nanoseconds]

-  File `lb` records a line per time step. a  The columns respectively denote [time stamp of the start of time step in nanoseconds], [time stamp of the end of the time step in nanoseconds], [a mesure of the minimum number of machines needed to host all the tasks hosted on the machines during this time step], [number of tasks arriving during this time step], [number of tasks hosted on the machines during this time step] 

