from random import shuffle
from const import *

class gTask(object):

    def __init__(self, a, tid, cpu, ram, dur, estDur):
        self.a = a
        self.tid = tid

        # We maintain both the actual duration
        # and the estimated duration.
        # along with their remaining versions
        self.dur = int(dur)
        self.remDur = int(dur)
        self.estDur = int(estDur)
        self.remEstDur = int(estDur)

        self.reqs = {CONST_LCPU : cpu, CONST_LRAM : ram}

        # Keeping track of the assignement
        self.m = None
        self.mo = None
        self.stTime = None

        self.jobId = str(self.tid)[:10]

    def __str__(self):
        if self.mo is None:
            return "t{0} arrived at {1}s, cpu {2}, ram {3}, dur {4}s, estDur {5}s".format(
                self.tid,
                self.a/float(CONST_SECINMILISEC),
                self.reqs[CONST_LCPU],
                self.reqs[CONST_LRAM],
                self.dur,
                self.estDur
                )
        else:
            return "t{0} arrived at {1}s, cpu {2}, ram {3}, dur {4}s, estDur {5}s, starts on M{6} at {7}s".format(
                self.tid,
                self.a/float(CONST_SECINMILISEC),
                self.reqs[CONST_LCPU],
                self.reqs[CONST_LRAM],
                self.dur,
                self.estDur,
                self.mo.idx,
                self.stTime/float(CONST_SECINMILISEC)
                )

# TODO : TOKEN.

class Machine(object):

    def __init__(self, idx, cpu, ram):
        self.idx  = idx
        self.capacities = {CONST_LCPU : cpu , CONST_LRAM : ram}
        self.usages = {CONST_LCPU : 0.0 , CONST_LRAM : 0.0}
        self.tasks = []
        self.lrt = 0.0
        self.cScore = 0

    def __str__(self):
        return "M {0} ({1}, {2})/({3}, {4}) - lrt : {5}".format(self.idx, self.usages[CONST_LCPU], self.usages[CONST_LRAM], self.capacities[CONST_LCPU], self.capacities[CONST_LRAM], self.lrt)

    def resetRequirements(self):
        self.usages = {CONST_LCPU : 0.0, CONST_LRAM : 0.0}

    def getRemainingCPUCap(self):
        return self.capacities[CONST_LCPU] - self.usages[CONST_LCPU]


def parseInstance(fName, floats = False):

    tasks = []

    with open(fName, "rt") as f:
        for line in f:
            line = line.split(',')
            if floats == False:
                t = gTask(int(line[0]), int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]))
            else:
                t = gTask(int(line[0]), int(line[1]), float(line[2]), float(line[3]), int(line[4]), int(line[5]))
            tasks.append(t)

    return tasks

def orderLTasks(lTasks, order):
    # NOTE : The Ordering is used by heuristics.
    # Therefor we must use the estimated time to order the items.
    if order == CONST_O_LIST:
        lTasks = lTasks
    elif order == CONST_O_RAND:
        shuffle(lTasks)
    elif order == CONST_O_DREQ:
        lTasks = sorted(lTasks, key=lambda t: t.reqs[CONST_LCPU], reverse = True)
    elif order == CONST_O_DDUR:
        lTasks = sorted(lTasks, key=lambda t: t.remEstDur, reverse = True)
    elif order == CONST_O_DDTR:
        lTasks = sorted(lTasks, key=lambda t: t.remEstDur * t.reqs[CONST_LCPU], reverse = True)
    else:
        assert(False), "Ordering on tasks not implemented : {0}".format(order)

    return lTasks

def getObjValue(lItems, lMachines):
    # The stats should be computed on the machines
    allT = [t.mo for t in lItems]
    if None in allT: assert(False)
    obj = 0.0
    for m in lMachines:
        lt = max([t.estDur for t in m.tasks] + [0.0])
        obj += lt * m.capacities[CONST_LCPU]
    return obj

def getActiveMachines(lMachines):
    return [m for m in lMachines if len(m.tasks) != 0]
