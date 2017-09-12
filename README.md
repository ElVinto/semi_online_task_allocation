# Semi Online Task Semi Online Task Allocation Simulator

This documents describes the different input parameters and output file of the semi-online simulator.

## Setup

This tool required python 2.7 and cplex v 12.6 or greater.

## Command Line
```
`python onlineSolver.py `
or 
`python onlineSolver.py  heuristic error timeStep ordering`
```

- `heu` is label denoting an solving heuristic adapted to the semi-online context. The list of possible heuristic label is presented in  next section "Adapted Bin Packing Heuristics". The default heuristic is FMF (First Merge Fit).

- `error` is an integer denoting of uncertainty in each task duration. Let d be the duration of a task, when the error is x, the expected duration utilised by heuristics is in between [d*(1-x%),d*(1+x%)]. The possible input errors in [0, 50, 100, 150, 200, 250, 350 400]. The default error is set to 0.

- `timeStep` is a positive integer denoting the time period in seconds of each time step in seconds. The default timeStep is set to 0.

- `ordering` is a label representing the default task ordering, ordering in [Dec,Inc]

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

## Output files

When running the simulator with the default argumet, i.e. `python onlineSolver.py ` four output files are created in the folder `./results/uncertain/`.
