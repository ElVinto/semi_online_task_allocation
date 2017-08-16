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
Implementation of sum of squares algorithm described in section 1.1.2of
 Sum-of-Squares Heuristics for bin Paching and Memory Allocation
 Michael A. Bender,  Bryan Bradley, Geetha Jagannathan, Kriashnan Pillaipakkanatt, 2001

 PRECONDITION : the machines are sorted by decreasing duration'''
def solve(h,lMachines, lItems, cTime, solution = None):

    st = time.clock()


    if len(lItems) == 0:
        return 0.0


    if len(lMachines) ==0:
        lMachines.append(Machine(0,1.0,1.0))



    # g is expressed in one tenth, g =k represents  the interval [k,k+1)
    g2lm ={}
    for g in range(10):
        g2lm[g]=[]
    for m in lMachines:
        gap = abs(m.capacities[CONST_LCPU] - m.usages[CONST_LCPU]- CONST_NUMIMPREC)
        g = int(gap*10)
        g2lm[g].append(m)


    maxIdxM = max(m.idx for m in lMachines)
    machineFound =False

    for i in lItems:
        # store the score of each machine
        best_m =None
        prev_g =None
        best_g=None
        best_val = sys.maxint
        # search the best bin
        for m in lMachines:

            cur_usage = m.usages[CONST_LCPU]
            if  solution is not None:
                for (t_lIdx,m_lIdx) in solution:
                    if m == lMachines[m_lIdx]:
                        cur_usage+=lItems[t_lIdx].reqs[CONST_LCPU]

            nv_usage = i.reqs[CONST_LCPU] + cur_usage

            if nv_usage <= m.capacities[CONST_LCPU]:
                cur_g = abs(int(10*(m.capacities[CONST_LCPU] - nv_usage - CONST_NUMIMPREC)))
                sumSquare = 0
                for g,lm in g2lm.iteritems():
                    if cur_g == g:
                        sumSquare += pow(len(lm)+1,2)
                    else:
                        sumSquare += pow(len(lm),2)

                if sumSquare<best_val:
                    best_m =m
                    best_val=sumSquare
                    best_g =cur_g
                    prev_g = abs(int(10*( m.capacities[CONST_LCPU] - cur_usage  - CONST_NUMIMPREC)))

        if best_m != None:
            if solution is None:
                h.assign(best_m, i, cTime)
            else:
                solution.append((lItems.index(i),lMachines.index(best_m)))

            g2lm[best_g].append(best_m)
            g2lm[prev_g].remove(best_m)


        else:

            maxIdxM+=1
            m = Machine(maxIdxM, 1.0, 1.0)
            lMachines.append( m)

            if solution is None:
                h.assign(m, i, cTime)
            else:
                solution.append((lItems.index(i),lMachines.index(m)))

            cur_g = abs(int(10*(m.capacities[CONST_LCPU] - i.reqs[CONST_LCPU] - CONST_NUMIMPREC)))
            g2lm[cur_g].append(m)


    end = time.clock()

    return end - st
