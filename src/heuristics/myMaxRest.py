'''
Created on 18 Mar 2017

@author: varmant
'''
import sys
import linecache
sys.path.append('../heuristics/')

from utils   import *
from heu     import *
from checker import *
import time

# Max rest is the same as worstFit and works as follows.
# Find the bin j with max spare capacity
# if item i fits in bin j assign i to j
# else; open a new bin.


def solve(h, lMachines, lItems, cTime, solution=None, crit = CONST_H_myMRR):
    # This implements best fit heuristic
    # Two variants are considered here.
    # Worst fit on requirement and on durations

    st = time.clock()

    if len(lItems) == 0:
        return 0.0

    maxIdxM = max(m.idx for m in lMachines)
    mOccupied = [m for m in lMachines if len(m.tasks) > 0.0]

    for i in lItems:
        # store the score of each machine
        worst_m =None
        worst_val = 0
        # search the best bin
        for m in mOccupied:

            cur_usage = m.usages[CONST_LCPU]
            if  solution is not None:
                for (t_lIdx,m_lIdx) in solution:
                    if m == lMachines[m_lIdx]:
                        cur_usage+=lItems[t_lIdx].reqs[CONST_LCPU]

            nv_usage = i.reqs[CONST_LCPU] + cur_usage

            if nv_usage <= m.capacities[CONST_LCPU]:
                if crit == CONST_H_myMRR:
                    # Worst fit on the requirements.
                    val = m.capacities[CONST_LCPU] - nv_usage
                    if val>worst_val:
                        worst_m =m
                        worst_val=val

                elif crit == CONST_H_myMRD:
                    # Worst fit in terms of durations
                    val = float(abs(m.lrt - i.remEstDur))
                    if val>worst_val:
                        worst_m =m
                        worst_val=val


        if worst_m != None:

            if solution is None:
                h.assign(worst_m, i, cTime)
            else:
                solution.append((lItems.index(i),lMachines.index(worst_m)))
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

