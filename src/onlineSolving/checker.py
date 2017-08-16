import sys
sys.path.append('../heuristics/')
from const import *

#

def computeObjForMachine(m, events, span, allTasks):
    
    assert(False), 'Func deprecated'
    
    sortedEvents = sorted(events, key = lambda e : e[3])
    #print "{0} tasks on machine {1}".format(len(sortedEvents), m)
    for e in sortedEvents:
        e[3] = int(e[3] / CONST_SECINMILISEC)
        e[4] = int(e[4] / CONST_SECINMILISEC)
    # For all the sorted events.
    tps = set([])
    for e in sortedEvents:
        tps = set(tps.union(set(range(e[3], e[4]))))
    return len(tps)


    
def parseTasks(finstance):
    
    assert(False), 'Func deprecated'
    
    allTasks = {}
    
    with open(finstance, "rt") as f:
        for line in f:
            line = line.split(", ")
            a, idx, dur = map(int, [line[0], line[1], line[4]])
            cpu, ram = map(float, [line[2],line[3]])            
            allTasks[idx] = [a, idx, cpu, ram, dur]

    return allTasks

def parseResults(fRes):
    
    assert(False), 'Func deprecated'
    
    ts = []    
    
    with open(fRes, "rt") as f:
        for line in f:
            tid, mid, a, st, ft = map(int, line.strip().split(", "))
            ts.append([tid, mid, a, st, ft])
    return ts
    

if __name__ == '__main__':
    
    fRes = "../../results/googleReal/res_hour2_FF_DDUR_2.csv"
    finstance = "../data/googleReal/hour2.csv"
    allTasks = parseTasks(finstance)
    ts = parseResults(fRes)
    
 
    nTasks = len(set([t[0] for t in ts]))
    nMachines = len(set([t[1] for t in ts]))
    rMach = set([t[1] for t in ts])


    print "nDiffTask : {0}".format(nTasks)
    print "nDiffMach : {0}".format(nMachines) 
    print "Mean WT : {0}".format(sum((t[3] - t[2]) / float(CONST_SECINMILISEC) for t in ts) / len(ts))
 
    
    totCost = 0
    
    for m in rMach:
        tMach = []
        
        for t in ts:
            if t[1] == m:
                # Tuple should be stored
                tMach.append(t)
        if len(tMach) == 0:
            assert(False)
        sc = computeObjForMachine(m, tMach, 2.0, allTasks)
        totCost += sc
    
    print "Total cost : {0}".format(totCost)
