import sys
import linecache
sys.path.append('../heuristics/')

from utils   import *
from heu     import *
from const     import *
from checker import *

import time


def initTmpStructures( lMachines, lItems, cTime):
    b2tasks  = {}
    m2b      = {}
    b2capa   = {}
    b2usage  = {}
    b2remDur = OrderedDict([])
    b2MaxStartTime = OrderedDict([])

    b = 0

    # Build bin struct from machines and items
    mOcc = [m for m in lMachines if m.usages[CONST_LCPU] != 0.0]
    for i, m in enumerate(mOcc):
        m2b[m]    = b
        b2capa[b]  = m.capacities[CONST_LCPU]
        b2usage[b] = sum([t.reqs[CONST_LCPU] for t in m.tasks])
        b2tasks[b]  = set(m.tasks)
        b2remDur[b] = max([t.remEstDur for t in m.tasks] + [0.0])
        b2MaxStartTime[b]= max([t.a for t in m.tasks])
        b += 1

    firstBinToAllocate = b

    for j in lItems:
        b2tasks[b]  = set([j])
        b2remDur[b] = j.remEstDur
        b2usage[b] = j.reqs[CONST_LCPU]
        b2capa[b]  = 1.0
        b2MaxStartTime[b]= j.a
        b += 1



    return b2tasks, m2b, b2capa, b2usage, b2remDur,b2MaxStartTime,firstBinToAllocate


def allcateBins( h,lMachines,cTime,m2b,b2tasks, droppedBins):
#         mOcc = [m for m in lMachines if m.usages[CONST_LCPU] != 0.0]
    mLibre = [m for m in lMachines if m.usages[CONST_LCPU] == 0.0]

    for m in m2b:
        b = m2b[m]
        for t in b2tasks[b]:
            if t not in m.tasks:
                h.assign(m, t, cTime)

    for b in b2tasks:
        if b not in droppedBins and b not in m2b.values():
                #print m2b.values()
                m = mLibre[0]
                for t in b2tasks[b]:
                    #print "assigningB {0} to {1}".format(t, m)
                    #assert(t is not None)
                    h.assign(m, t, cTime)
                mLibre.remove(m)

''' SEQUENTIAL BIN FILLING METHODS '''
def solve(h,lMachines, lItems, cTime):

    b2tasks, m2b, b2capa, b2usage, b2remDur,b2MaxTaskId,firstBinToAllocate = initTmpStructures(lMachines, lItems, cTime)

    # Start algo

    #b2remDur = OrderedDict(sorted(b2remDur.items(), key=operator.itemgetter(1), reverse = True))

    st = time.clock()
    b2MaxTaskId = OrderedDict(sorted(b2MaxTaskId.items(), key=operator.itemgetter(1), reverse = True))

    binsToVisit = b2MaxTaskId.keys()
    mergedBins = []
    while len(binsToVisit) != 0:

        bi = binsToVisit[0]
        binsToVisit.remove(bi)

        # NOTE : Optimize here with starting index

        bj,j = nextAllocableWith(bi, binsToVisit, b2usage, b2capa, firstBinToAllocate,0)

        while bj != None:
            bd, br = mergeIn(bi, bj, b2tasks, firstBinToAllocate, b2usage, b2remDur)
            #print br, b2usage[br], "\n", "\n".join(map(str, b2tasks[br]))
            mergedBins.append(bd)
            binsToVisit.remove(bj)

            bi = br
            bj,j = nextAllocableWith(bi, binsToVisit, b2usage, b2capa, firstBinToAllocate,j)


    allcateBins(h,lMachines,cTime,m2b,b2tasks, mergedBins)

    end = time.clock()

    return end - st


def nextAllocableWith(  bi, binsToVisit, b2usage, b2capa, firstBinToAllocate, startIdx):
    #print binsToVisit

    for j in range(startIdx, len(binsToVisit)):
        bj = binsToVisit[j]
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
            return bj,j

    return None,-1


def mergeIn(  bi, bj, b2tasks, firstBinToAllocate, b2usage, b2remDur):

    if bi < firstBinToAllocate:
        br = bi
        bs = bj
    else:
        br = bj
        bs = bi

    b2tasks[br] = b2tasks[br].union(b2tasks[bs])
    b2usage[br] = b2usage[br] + b2usage[bs]
#     b2remDur[br] = max( b2remDur[br], b2remDur[bs])

    return bs, br
