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



curPtrM = None

def solve(h, lMachines, lItems, cTime, solution = None):

    st = time.clock()

    global curPtrM
    if curPtrM is None:
        curPtrM = 0

#     print curPtrM, len(lMachines)

    maxIdxM = max(m.idx for m in lMachines)


    mOccupied = [m for m in lMachines if len(m.tasks) > 0]
    if len(mOccupied)<=curPtrM:
        curPtrM = 0

    if len(mOccupied) == 0:
        if len(lMachines)==0:
            lMachines.append( Machine(0, 1.0, 1.0))
        curPtrM = 0
        m = lMachines[curPtrM]
        mOccupied.append(m)


    startCurPtrM = curPtrM # OFF BY ONE ?

    m = mOccupied[curPtrM]
    noOccupiedMachineFit =False
    for i in lItems:

        cur_usage = m.usages[CONST_LCPU]
        if  solution is not None:
            for (t_lIdx,m_lIdx) in solution:
                if m == lMachines[m_lIdx]:
                    cur_usage += lItems[t_lIdx].reqs[CONST_LCPU]
        nv_usage = i.reqs[CONST_LCPU] + cur_usage

        # Search the next fitting machine
        while nv_usage > m.capacities[CONST_LCPU]:

            if curPtrM == len(mOccupied) - 1:
                curPtrM = 0
            else:
                curPtrM += 1

            if startCurPtrM == curPtrM:
                noOccupiedMachineFit = True
                break


            # looping
            m = mOccupied[curPtrM]
            cur_usage = m.usages[CONST_LCPU] ## ??
            if solution is not None:
                for (t_lIdx,m_lIdx) in solution:
                    if m == lMachines[m_lIdx]:
                        cur_usage += lItems[t_lIdx].reqs[CONST_LCPU]
            nv_usage = i.reqs[CONST_LCPU] + cur_usage

        # No machine hosting at least a task can host the item
        if noOccupiedMachineFit:
            # A new machine new or empty machine has to chosen
            if len(mOccupied) == len(lMachines):
#                 print " create new M{0}".format(m.idx)
                maxIdxM+=1
                lMachines.append( Machine(maxIdxM, 1.0, 1.0))

            # add the task to an empty machine
#             print " add {0} to empty M{1}".format(i.tid,m.idx)
            m =  lMachines[len(mOccupied)]
            if solution is None:
                h.assign(m, i, cTime)
            else:
                solution.append((lItems.index(i),lMachines.index(m)))
            mOccupied.append(m)
            startCurPtrM = len(mOccupied)-1
            curPtrM = startCurPtrM
            noOccupiedMachineFit =False

        else:

#             print "add {0} to occupied M{1}".format( i.tid, m.idx)

            if solution is None:
                h.assign(m, i, cTime)
            else:
                solution.append((lItems.index(i),lMachines.index(m)))
            startCurPtrM =curPtrM
            m = mOccupied[curPtrM]


    end = time.clock()

    return end - st
