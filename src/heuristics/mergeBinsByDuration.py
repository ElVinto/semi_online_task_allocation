import sys
import linecache
sys.path.append('../heuristics/')

from utils   import *
from heu     import *
from checker import *
from const import *
from collections import OrderedDict
from operator import *
from heu import *


def initTmpStructures(lMachines, lItems, cTime):
    b2tasks  = {}
    m2b      = {}
    b2capa   = {}
    b2usage  = {}
    b2remDur = OrderedDict([])

    b = 0

    # Build bin struct from machines and items
    mOcc = [m for m in lMachines if m.usages[CONST_LCPU] != 0.0]
    for i, m in enumerate(mOcc):
        m2b[m]    = b
        b2capa[b]  = m.capacities[CONST_LCPU]
        b2usage[b] = sum([t.reqs[CONST_LCPU] for t in m.tasks])
        b2tasks[b]  = set(m.tasks)
        b2remDur[b] = max([t.remdur for t in m.tasks] + [0.0])
        b += 1

    firstBinToAllocate = b

    for j in lItems:
        b2tasks[b]  = set([j])
        b2remDur[b] = j.remdur
        b2usage[b] = j.reqs[CONST_LCPU]
        b2capa[b]  = 1.0
        b += 1

    b2remDur = OrderedDict(sorted(b2remDur.items(), key=itemgetter(1), reverse = True))

    return b2tasks, m2b, b2capa, b2usage, b2remDur,firstBinToAllocate


def allcateBins(h,lMachines,cTime,m2b,b2tasks, droppedBins):
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

''' FLEXIBLE FIT METHODS '''

def solve(h, lMachines, lItems, cTime):

    b2tasks, m2b, b2capa, b2usage, b2remDur,firstBinToAllocate = initTmpStructures(lMachines, lItems, cTime)

    # create a function initializing And updating b2Weigth
    # create a function updating binsTovisit
    binsToVisit = b2remDur.keys()
    mergedBins = []

    bs, br =  getBestMergeableBinsAndUpdate(binsToVisit,b2capa,b2usage,b2remDur, firstBinToAllocate)
    while bs !=-1 and br !=-1 :
        b2tasks[br] = b2tasks[br].union(b2tasks[bs])
        b2usage[br] = b2usage[br] + b2usage[bs]
        b2remDur[br] = max( b2remDur[br], b2remDur[bs])
        mergedBins.append(bs)
        if bs in binsToVisit:
            binsToVisit.remove(bs)
        bs, br = getBestMergeableBinsAndUpdate(binsToVisit,b2capa,b2usage,b2remDur, firstBinToAllocate)

        # call the update function

    allcateBins(h,lMachines,cTime,m2b,b2tasks, mergedBins)


def getBestMergeableBinsAndUpdate(bToVisit,b2capa,b2usage,b2weight,firstBinToAllocate):
    unMergeableBins =[]
    maxW = 0
    maxBs = -1
    maxBr = 1
    for i in range(len(bToVisit)-1):
        bi = bToVisit[i]
        if bi in unMergeableBins :
            continue
        biIsMergeable = False
        for j in range(i+1,len(bToVisit)):
            bj = bToVisit[j]

            if bj in unMergeableBins :
                continue

            if bi == bj:
                continue

            if  bj < firstBinToAllocate and bi < firstBinToAllocate:
                continue

            if bi < firstBinToAllocate:
                br = bi
                bs = bj
            else:
                br = bj
                bs = bi

            if b2usage[br] + b2usage[bs] > b2capa[br]:
                continue

            biIsMergeable = True
            wbsbr =b2weight[bs]+ b2weight[br]
            if(maxW<wbsbr):
                maxW =wbsbr
                maxBr = br
                maxBs = bs

        if not biIsMergeable:
            unMergeableBins.append(bi)

    for b in unMergeableBins:
        bToVisit.remove(b);

    return maxBs, maxBr







