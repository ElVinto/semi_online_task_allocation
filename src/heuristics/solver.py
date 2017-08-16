from sys import argv
from heu import *
from const import *
from utils import *
from time import clock


if __name__ == "__main__":
       
    # Parsing the instance
    nPass = str(argv[1]).split("_")[2].split('.')[0]    
    
    solvMeth = str(argv[2])
    taskOrdering = str(argv[3])
    timeOut = float(argv[4])
    bench = str(argv[5])
    
    # Build up the machines.
    if bench == "integerInstances":
        #assert(False)
        CONST_CAP = 100
        lItems = parseInstance(str(argv[1]), False)
        lMachines = [Machine(i + 1, CONST_CAP, CONST_CAP) for i in range(len(lItems))]    
    else:
        CONST_CAP = 0.5
        lItems = parseInstance(str(argv[1]), True)    
        lMachines = [Machine(i + 1, CONST_CAP, CONST_CAP) for i in range(len(lItems))]  
    
    lItems = orderLTasks(lItems, taskOrdering)
    panic = sum([i.dur * CONST_CAP for i in lItems])
    solver = heu(solvMeth, timeOut)
    
    fileOut = "../../results/{0}/approx/result_{1}_{2}.csv".format(bench, solvMeth, taskOrdering)
    
    n = len(lItems)
    
    if solver.solve(lItems, lMachines):
        obj = getObjValue(lItems, lMachines)
    else:
        obj = panic
        
    print "{0}, {1}, {2}, {3}, {4}, {5}".format(n, nPass, obj, timeOut, timeOut, clock())
    with open(fileOut, "at") as f:
        print >> f, "{0}, {1}, {2}, {3}, {4}, {5}".format(n, nPass, obj, timeOut, timeOut, clock())
    
            
