# Semi Online Task Semi Online Task Allocation Simulator

This documents describes the different input parameters and output file of the semi-online simulator.

## Setup

This tool required python 2.7 and cplex v 12.6 or greater.

## Command Line
```
`cd src/onlineSolving/`
then
`python onlineSolver.py`
or 
`python onlineSolver.py  heu err timeStep ordering`
```

- `heu` is label denoting an solving heuristic adapted to the semi-online context. The list of possible heuristic label is presented in  next section "Adapted Bin Packing Heuristics". The default heuristic is FMF (First Merge Fit).

- `err` is an integer denoting of uncertainty percertage in each task duration. Let d be the duration of a task, when the error is x, the expected duration utilised by heuristics is in between [d*(1-x%),d*(1+x%)]. The possible input errors in [0, 50, 100, 150, 200, 250, 350 400]. The default error is set to 0.

- `timeStep` is a positive integer denoting the time period in seconds of each time step in seconds. The default timeStep is set to 0.

- `ordering` is a label representing the task ordering. The default task ordering is DDUR (Decreasing Duration), the different options are listed in the section Ordering.

## Adapted bin Packing Heuristics
- `my_FF`: First Fit
- `myBFD`: Best Fit on Duration
- `myBFR`: Best Fit on Requirement
- `myNF`: Next Fit 
- `myMRR`: Max Rest on Requirement
- `myMRD`: Max Rest on Duration
- `mySS`: Sum Square
- `myHA`: Harmonic
All the above heuristics can be ran as the input of a RNIS local search algorithm implemented in  CPLEX. For this purpose, the heuristic label has to be followed by `_CPLEX`. Consequently the following heuristic strategies are also available: `FMF_CPLEX`, `myFF_CPLEX`, `myBFD_CPLEX`, `myBFR_CPLEX`, `myNF_CPLEX`, `myMRR_CPLEX`,`myMRD_CPLEX`, `mySS_CPLEX`, `myHA_CPLEX`.

## Ordering
- `LIST` chronological order of the 
- `RAND` random
- `DREQ` decreasing cpu requirement
- `DDUR` decreasing duration
- `DDTR` decreasing duration then requirement

## Input file
When launching the command line `python onlineSolver.py heu err timeStep ordering`, the simulator will the file "./src/data/allTasks_U`err`.csv". Each line of this file specifies the characteristics of an incoming task. The columns represents for each task: the arrival time stamp (in nano seconds), the task Id, the cpu requirement (percentage), the ram requirement (percentage), the  duration (in seconds), the expected duration (in seconds).

## Output files

When launching the command line `python onlineSolver.py heu err timeStep ordering`, the simulator creates four output files  in the folder "./results/uncertain/", all terminating by "_alltasks_U`err`_`heu`_`ordering`_`timeStep`.csv".
- the columns of the file `usage` respectively denote startOfWindow, endOfWindow, numMachinesInUse, objFunction
- the columns of the file `res` respectively denote taskId, machineId, taskArrivalTime, taskStartingTime, taskFinishingTime
- the columns of the file `lb` respectively denote startOfWindow, endOfWindow, lowerBoundOnObj, numTasksInBucket, numTasksInSimulation
