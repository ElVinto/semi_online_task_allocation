import sys
import linecache
sys.path.append('../heuristics/')

from utils   import *
from heu     import *
from checker import *

from heu import *

def initTmpStructures(self,heu,lMachines, lItems, cTime):
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

    b2remDur = OrderedDict(sorted(b2remDur.items(), key=operator.itemgetter(1), reverse = True))

    return b2tasks, m2b, b2capa, b2usage, b2remDur,firstBinToAllocate



def allcateBins(self,lMachines,cTime,m2b,b2tasks, droppedBins):
#         mOcc = [m for m in lMachines if m.usages[CONST_LCPU] != 0.0]
    mLibre = [m for m in lMachines if m.usages[CONST_LCPU] == 0.0]

    for m in m2b:
        b = m2b[m]
        for t in b2tasks[b]:
            if t not in m.tasks:
                self.assign(m, t, cTime)

    for b in b2tasks:
        if b not in droppedBins and b not in m2b.values():
                #print m2b.values()
                m = mLibre[0]
                for t in b2tasks[b]:
                    #print "assigningB {0} to {1}".format(t, m)
                    #assert(t is not None)
                    self.assign(m, t, cTime)
                mLibre.remove(m)

''' FLEXIBLE FIT METHODS '''

def flexibleFit(self,lMachines, lItems, cTime):
    b2tasks, m2b, b2capa, b2usage, b2remDur,firstBinToAllocate = self.initTmpStructures(lMachines, lItems, cTime)

    # create a function initializing And updating b2Weigth
    # create a function updating binsTovisit

    binsToVisit, b2weight =  self.initOrder(b2capa,b2usage,b2remDur)

    mergedBins = []
    while len(binsToVisit) != 0:

        bi = binsToVisit[0]
        # bi stay in the list it

        bj = self.nextAllocableWith(bi, binsToVisit, b2usage, b2capa, firstBinToAllocate)
        # bj will be merged with bj

        if bj != None:
            bs, br = self.mergeIn(bi, bj, b2tasks, firstBinToAllocate, b2usage)
            #print br, b2usage[br], "\n", "\n".join(map(str, b2tasks[br]))
            mergedBins.append(bs)
            binsToVisit.remove(bs)
        else:
            binsToVisit.remove(bi)

        # call the update function

    self.allcateBins(lMachines,cTime,m2b,b2tasks, mergedBins)

    return None


def initOrder(self,b2capa,b2usage,b2remDur):
    b2weight = OrderedDict([])
    aOfbins = b2capa.keys()
    for i,bi in range(len(aOfbins)-1):
        maxWbi = 0;
        for j,bj in range(i+1,len(aOfbins)):
            wbibj =b2remDur[bi]+ b2remDur[bj]
            if(maxWbi<wbibj):
                maxWbi =wbibj
        b2weight[bi]=maxWbi

    b2weight = OrderedDict(sorted(b2weight.items(), key=operator.itemgetter(1), reverse = True))
    binsToVisit = b2weight.keys()

    return binsToVisit, b2weight


'''  remove the bin bs (bin sender) and update the weight of br (bin receiver) and the remining bins in b2Weight '''
def remBinAndUpdateOrder(self,bs,br,binsToVisit,b2weight,b2capa,b2usage):
    # Note the ordering need be optimized, we do not need to reorder all the value

    # merge bi and bj

    b2weight = OrderedDict([])
    aOfbins = b2capa.keys()
    for i,bi in range(len(aOfbins)-1):
        maxWbi = 0;
        for j,bj in range(i+1,len(aOfbins)):
            wbibj =b2weight[bi]+ b2weight[bj]
            if(maxWbi<wbibj):
                maxWbi =wbibj
        b2weight[bi]=maxWbi

    b2weight = OrderedDict(sorted(b2weight.items(), key=operator.itemgetter(1), reverse = True))
    binsToVisit = b2weight.keys()

    # return a new bi,bi to explore
    return binsToVisit, b2weight



''' SEQUENTIAL BIN FILLING METHODS '''
def fillMachineFirst(self,lMachines, lItems, cTime):

    b2tasks, m2b, b2capa, b2usage, b2weight,firstBinToAllocate = self.initTmpStructures(lMachines, lItems, cTime)
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


    self.allcateBins(lMachines,cTime,m2b,b2tasks, mergedBins)


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
