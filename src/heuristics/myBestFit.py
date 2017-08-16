'''
Created on 4 Mar 2017

@author: varmant
'''
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

def solve(h, lMachines, lItems, cTime, solution=None, crit = CONST_H_myBFR):
    # This implements best fit heuristic
    # Three variants are considered here.
    # Best fit on reqs, on durations or on duration * reqs

    st = time.clock()

    if len(lItems) == 0:
        return 0.0

    maxIdxM = max(m.idx for m in lMachines)
    mOccupied = [m for m in lMachines if len(m.tasks) > 0.0]

    for i in lItems:
        # store the score of each machine
        best_m =None
        best_val = sys.maxint
        # search the best bin
        for m in mOccupied:

            cur_usage = m.usages[CONST_LCPU]
            if  solution is not None:
                for (t_lIdx,m_lIdx) in solution:
                    if m == lMachines[m_lIdx]:
                        cur_usage+=lItems[t_lIdx].reqs[CONST_LCPU]

            nv_usage = i.reqs[CONST_LCPU] + cur_usage

            if nv_usage <= m.capacities[CONST_LCPU]:
                if crit == CONST_H_myBFR:
                    # Best fit on the requirements.
                    val = m.capacities[CONST_LCPU] - nv_usage
                    if val<best_val:
                        best_m =m
                        best_val=val

                elif crit == CONST_H_myBFD:
                    # This measures the distance in terms of durations
                    val = float(abs(m.lrt - i.remEstDur))
                    if val<best_val:
                        best_m =m
                        best_val=val



        if best_m != None:
            if solution is None:
                h.assign(best_m, i, cTime)
            else:
                solution.append((lItems.index(i),lMachines.index(best_m)))
        else:
            # A new machine new or empty machine has to chosen
            if len(mOccupied) == len(lMachines):
                maxIdxM+=1
                lMachines.append( Machine(maxIdxM, 1.0, 1.0))

            # add the task to an empty machine

            m =  lMachines[len(mOccupied)]
#             assert len(m.tasks)==0
            if solution is None:
                h.assign(m, i, cTime)
            else:
                solution.append((lItems.index(i),lMachines.index(m)))
            mOccupied.append(m)


    # Sorting the list of machines here.
    end = time.clock()
    return end - st

