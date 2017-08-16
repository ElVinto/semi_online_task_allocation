'''
Created on 1 Mar 2017

@author: varmant
'''
import sys
import linecache
sys.path.append('../heuristics/')

from utils   import *
from heu     import *
from checker import *
import time

def nextAllocableWith(self, bi, binsToVisit, b2usage, b2capa, firstBinToAllocate):
    #print binsToVisit
    for bj in binsToVisit:
        if bi == bj:
            continue

        if  bj < firstBinToAllocate and bi < firstBinToAllocate:
            continue

        if bi < firstBinToAllocate:
            br = bi
            bd = bj
        else:
            br = bj
            bd = bi


        if b2usage[br] + b2usage[bd] <= b2capa[br]:
            return bj

    return None

def mergeIn(self, bi, bj, b2tasks, firstBinToAllocate, b2usage):

    if bi < firstBinToAllocate:
        br = bi
        bd = bj
    else:
        br = bj
        bd = bi

    b2tasks[br] = b2tasks[br].union(b2tasks[bd])
    b2usage[br] = b2usage[br] + b2usage[bd]

    return bd, br


def solve(self, lMachines, lItems, cTime):

    b2tasks  = {}
    m2b      = {}
    b2capa   = {}
    b2usage  = {}
    b2weight = OrderedDict([])

    b = 0

    # Build bin struct from machines and items

    mOcc = [m for m in lMachines if m.usages[CONST_LCPU] != 0.0]
    mLibre = [m for m in lMachines if m.usages[CONST_LCPU] == 0.0]

    for i, m in enumerate(mOcc):
        m2b[m]    = b
        b2capa[b]  = m.capacities[CONST_LCPU]
        b2usage[b] = sum([t.reqs[CONST_LCPU] for t in m.tasks])
        b2tasks[b]  = set(m.tasks)
        b2weight[b] = max([t.remEstDur for t in m.tasks] + [0.0])
        b += 1

    firstBinToAllocate = b


    if len(lItems) == 0:
        return 0.0

    st = time.clock()

    for j in lItems:
        b2tasks[b]  = set([j])
        b2weight[b] = j.remEstDur
        b2usage[b] = j.reqs[CONST_LCPU]
        b2capa[b]  = 1.0
        b += 1

    b2weight = OrderedDict(sorted(b2weight.items(), key=operator.itemgetter(1), reverse = True))

    # Start algo
    binsToVisit = b2weight.keys()
    mergedBins = []
    while len(binsToVisit) != 0:

        bi = binsToVisit[0]
        binsToVisit.remove(bi)

        # NOTE : Optimize here with starting index
        bj = self.nextAllocableWith(bi, binsToVisit, b2usage, b2capa, firstBinToAllocate)

        while bj != None:
            bd, br = self.mergeIn(bi, bj, b2tasks, firstBinToAllocate, b2usage)
            #print br, b2usage[br], "\n", "\n".join(map(str, b2tasks[br]))
            mergedBins.append(bd)
            binsToVisit.remove(bj)

            bi = br
            bj = self.nextAllocableWith(bi, binsToVisit, b2usage, b2capa, firstBinToAllocate)


    for m in m2b:
        b = m2b[m]
        for t in b2tasks[b]:
            if t not in m.tasks:
                self.assign(m, t, cTime)


    for b in b2tasks:
        if b not in mergedBins and b not in m2b.values():
            #print m2b.values()

            m = mLibre[0]
            for t in b2tasks[b]:
                #print "assigningB {0} to {1}".format(t, m)
                #assert(t is not None)
                self.assign(m, t, cTime)
            mLibre.remove(m)
    end = time.clock()

    return end  - st
