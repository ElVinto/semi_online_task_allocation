'''
Created on 15 Mar 2017

@author: varmant
'''
import sys
import linecache
sys.path.append('../heuristics/')

from utils   import *
from heu     import *
from checker import *
import time


'''
 Algorithm based on A simple Online Bin backing Algorithm
 C. C. Lee and D. T. Lee, Journal of the Association for Computing Machinery, 1985
 PRECONDITION : the machines are sorted by decreasing duration
 '''
def solve(h,lMachines, lItems, cTime, solution=None):
    st = time.clock()

    if len(lItems) == 0:
        return 0.0


    if len(lMachines) ==0:
        lMachines.append(Machine(0,1.0,1.0))


    # init the structures mapping each interval k, to its bounds and its associated machine
    k2lb = {}
    k2ub ={}
    k2m ={}
    for  offset_m,m in enumerate(lMachines):
        k= offset_m +1
        if k< len(lMachines):
            k2lb[k] = 1.0/float(1.0+k)
        else:
            k2lb[k] =0.0
        k2ub[k] = 1.0/float(k)
        k2m[k] =m



    maxRemEstDur = abs(float(max(t.remEstDur for t in lItems)))
    maxIdxM = max(m.idx for m in lMachines)

    for i in lItems:
        machineFound = False
        kFound = -1
        # normalised weight of an item
        if maxRemEstDur ==0:
            ai =0
        else:
            ai = max(0, i.remEstDur) / (maxRemEstDur)
        # select the machine
        for k,m in k2m.iteritems():
            if k2lb[k]-CONST_NUMIMPREC < ai and ai<=k2ub[k]+ CONST_NUMIMPREC:
                kFound =k
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
                    machineFound = True
                break
        if not machineFound :
            maxIdxM += 1
            mvM = Machine(maxIdxM, 1.0, 1.0)
            lMachines.append(mvM)
            k2m[kFound] = mvM
            if solution is None:
                h.assign(mvM, i, cTime)
            else:
                solution.append((lItems.index(i),lMachines.index(mvM)))

        assert kFound!=-1, str(k2lb)

    end = time.clock()

    return end - st
