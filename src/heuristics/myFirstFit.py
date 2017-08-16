'''
Created on 4 Mar 2017

@author: varmant
'''
import sys
import linecache
sys.path.append('../heuristics/')

from utils   import *
from heu     import *
from checker import *
import time


def solve(h,lMachines, lItems, cTime, solution=None):
    
    st = time.clock()

    if len(lItems) == 0:
        return 0.0

    maxIdxM = max(m.idx for m in lMachines)
    machineFound =False

    for i in lItems:
        machineFound =False
        for m in lMachines:

            cur_usage = m.usages[CONST_LCPU]
            if  solution is not None:
                for (t_lIdx,m_lIdx) in solution:
                    if m == lMachines[m_lIdx]:
                        cur_usage+=lItems[t_lIdx].reqs[CONST_LCPU]

            nv_usage = i.reqs[CONST_LCPU] + cur_usage
            if nv_usage <= m.capacities[CONST_LCPU]:
                if solution is None:
                    h.assign(m, i, cTime)
                else:
                    solution.append((lItems.index(i),lMachines.index(m)))
                machineFound =True
                break
        if not machineFound :
            maxIdxM+=1
            mvM = Machine(maxIdxM, 1.0, 1.0)
            lMachines.append(mvM)
            if solution is None:
                h.assign(mvM, i, cTime)
            else:
                solution.append((lItems.index(i),lMachines.index(mvM)))


    end = time.clock()

    return end - st
