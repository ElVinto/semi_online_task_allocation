import sys
import os
import linecache
import math
sys.path.append('../heuristics/')

from utils import *
from heu import *
from const import *
from lb import *


"""
TODO : Reduce the number of machine for BF series to perform better.
"""

class Mon(object):


    def __init__(self, dFiles, bucketSize, endObsWindow, lMachines):

        self.fName = dFiles[CONST_F_IN] # Source of fata
        self.fNameOut = dFiles[CONST_F_SOL]  # Source of fata
        self.fNameOutUsage = dFiles[CONST_F_USAGE]  # Source of fata
        self.fNameOutLb = dFiles[CONST_F_LB]  # Source of fata
        self.fNameOutTiming = dFiles[CONST_F_TIME]
        self.fNameOutCplex = dFiles[CONST_F_CPLEX]

        self.bucketSize = bucketSize # In seconds

        self.cTime  = int(linecache.getline(self.fName, 1).strip().split(", ")[0])
        self.cTime  = int(math.floor(self.cTime / CONST_SECINMILISEC))
        self.cTime  = self.cTime - self.cTime%bucketSize
        self.cTime  = self.cTime * CONST_SECINMILISEC
        self.stTime = self.cTime


        self.lMachines = lMachines   # List of machines
        self.nBuscketsSoFar = 0
        self.nTasksSoFar = 0
        self.totCost = 0
        self.LB = 0
        self.bucketSize = bucketSize
        self.endObsWindow = endObsWindow

        with open(fIn) as f: self.nLines = sum(1 for line in f)
        self.timeSpampD = int(linecache.getline(self.fName, self.nLines).strip().split(", ")[0])

        # Keeping track.
        # - This is updated after reading a bucket.
        self.nTasksInBucket = 0



    def getNextTasks(self, lastTaskLine):

        nextBunch = []



#         if nextTaskLine == 0:
#             cts = int(linecache.getline(self.fName, 1).strip().split(", ")[0])
#         else:
#             cts = int(linecache.getline(self.fName, nextTaskLine).strip().split(", ")[0])


        nextTaskLine = lastTaskLine +1;
        line = linecache.getline(self.fName, nextTaskLine).strip().split(", ")


        while line[0] !='':
            cts, tid, dur, estDur = map(int, [line[0], line[1], line[4], line[5]])

#             print "next task arrival {0} current time {1}".format(cts,self.cTime)
            if  cts >= int(self.cTime) and cts < int(self.cTime + self.bucketSize * CONST_SECINMILISEC):
                cpu, ram = map(float, [line[2], line[3]])
                if cpu <0.0:
#                     print "ignoring negative cpu: ", cpu
                    nextTaskLine += 1;
                    line = linecache.getline(self.fName, nextTaskLine).strip().split(", ")
                    continue
                if dur <0.0:
#                     print "ignoring negative duration: ",dur
                    nextTaskLine +=1;
                    line = linecache.getline(self.fName, nextTaskLine).strip().split(", ")
                    continue
                if estDur <0.0:
#                     print "ignoring negative estimate duration: ",estDur
                    nextTaskLine +=1;
                    line = linecache.getline(self.fName, nextTaskLine).strip().split(", ")
                    continue

                nextBunch.append(gTask(cts, tid, cpu, ram, dur , estDur))
    #             print 'line '+linecache.getline(self.fName, nextTaskLine)
    #             print ' cTime '+str(self.cTime)
    #             print ' bucket size '+str(self.bucketSize * CONST_SECINMILISEC)

                nextTaskLine += 1
                line = linecache.getline(self.fName, nextTaskLine).strip().split(", ")
            else:
                nextTaskLine -= 1
                break

#             if line[0] !='':
#                 cts, tid, dur, estDur = map(int, [line[0], line[1], line[4], line[5]])

        self.nBuscketsSoFar += 1
        self.nTasksSoFar += len(nextBunch)
        self.cTime = self.cTime + self.bucketSize * CONST_SECINMILISEC
#         print len(nextBunch)
        self.nTasksInBucket = len(nextBunch)
#         print "=== NT ==="
#         print "ADD {0}".format(len(nextBunch))
        return nextBunch, nextTaskLine

    def updateRemTimes(self):
        if verb: print "\tupdate remaining times allocated tasks"
        # RECALL self.cTime is the start of the bucket,  cTime+bucketSize*Cnst = end of the bucket
        # update the task remaining time to the end of the bucket
        for m in self.lMachines:
            for t in m.tasks:
                # Update remaining duration
                t.remDur = (t.stTime + t.dur * CONST_SECINMILISEC - (self.cTime+self.bucketSize * CONST_SECINMILISEC) )/ float(CONST_SECINMILISEC)
                t.remDur = max(t.remDur, 0)

                # Update remaing estimated duration
                t.remEstDur = (t.stTime + t.estDur * CONST_SECINMILISEC - (self.cTime+self.bucketSize * CONST_SECINMILISEC))/ float(CONST_SECINMILISEC)
                t.remEstDur = max(t.remEstDur, 0)

                if verb:print "\t\t {0} \tremDur:{1}".format(t,t.remDur)

            if len(m.tasks)>0:
                m.lrt = max(t.remEstDur for t in m.tasks)
            else:
                m.lrt =0


    def dumpLowerBound(self, verb):
        """
            The lower bound is computed piece wise at the end of each bucket.
            1/ all tasks that should be considered in this bucket (arriving + runing)
            are merged.
            2/ We find a lower bound on the allocated space for this set of tasks.
            3/ It is a relaxation because of two things.
                - We relax the "no migration" constraint
                - We relax the "no divisibility" constraint
        """

        allTasksInBucket =  [t for m in self.lMachines for t in m.tasks]

        if len(allTasksInBucket) == 0:
            lb = 0.0
            if verb: print "\t0 seconds is the LB2 allocated in current bucket "
        else:
            lb = lb2_inBucket(allTasksInBucket, self.bucketSize, 1.0, self.cTime,verb)
        #print "Got for lb"
        ct = self.cTime / float(CONST_SECINMILISEC)
        nct = ct + self.bucketSize
        self.LB += lb

        #  - record the number of tasks arrived, nb of tasks running, in dump LB
        #  - record the number of runing tasks on all machiens
        self.nTasksInSys = 0
        for m in self.lMachines:
            for t in m.tasks:
                self.nTasksInSys += 1

#         print int(ct), int(nct), "->", self.nTasksInSys

        with open(self.fNameOutLb, 'at') as f:
            print >> f, "{0}, {1}, {2}, {3}".format(int(ct), int(nct), lb, self.nTasksInBucket, self.nTasksInSys)

        return lb

    def dumpTimings(self, verb, buf, s):

        ct = self.cTime / float(CONST_SECINMILISEC)
        nct = ct + self.bucketSize
        aMa = [m for m in self.lMachines if m.usages[CONST_LCPU] > 0.00001]

        if s < 0.0001:
            s = 0.0000

        with open(self.fNameOutTiming, 'at') as f:
            print >> f, "{0}, {1}, {2}, {3}, {4}".format(int(ct), int(nct), len(buf), len(aMa), round(s, 4))


    def dumpObjFunction(self, verb):
        """
        This will compute the objective function
        over the last bucketSize seconds.
        NOTE : This function should be called before any clean
        up happening on machines.
        NOTE : We dump the following :
        - TimeStampSt, TimeStampEnd, nMachinesInUse, score
        """

        ct = self.cTime
        nct = ct + self.bucketSize * CONST_SECINMILISEC
        machInUse = [m for m in self.lMachines if len(m.tasks) > 0.0]

        score = 0
        for m in machInUse:
            maxmscore = 0
            for t in m.tasks:
                # RECALL self.cTime is the started time of the bucket
                # RECALL t.remDur has not been updated yet


                    # tasks  finishing after the bucket
                    if t.stTime + t.dur * CONST_SECINMILISEC - self.cTime > bucketSize * CONST_SECINMILISEC:
                        maxmscore= self.bucketSize
                        break

                    else:
                        # RECALL m.lrt > 0.0 ensures that (t.stTime + t.dur * CONST_SECINMILISEC - cTime > 0 )

                        # tasks finishing between ]cTime,cTime+bucketSize]
                        mscore = (t.stTime + t.dur * CONST_SECINMILISEC - self.cTime) / CONST_SECINMILISEC
                        if mscore > maxmscore:
                            maxmscore = mscore

            if maxmscore > 0:
                m.cScore += maxmscore
                mCost = maxmscore
                score += mCost

        self.totCost += score


        with open(self.fNameOutUsage, "at") as f:
            print >> f, "{0}, {1}, {2}, {3}".format(int(ct), int(nct), len(machInUse), score)
        if verb: print "\t{0} seconds is really allocated in current bucket".format(score)

        return score

    def removeOldTasks(self, verb):
        #if verb:
            #print "\033[92mUpdated {0} tasks\033[0m".format(n)

        removed = 0
        tRemoved = []

        #if a tasks has been assigned
        #t.stTime != None
        for m in self.lMachines:

            rem = False

            for t in m.tasks:
                #print t.remDur, self.bucketSize

                # RECALL self.cTime is the start of the bucket,  cTime+bucketSize*Cnst = end of the bucket
                # RECALL t.remDur has been updated considering the end of the bucket and can be used
                # remove tasks finishing before and at the end of the bucket
                if t.remDur <= 0.0:

                    #print "TG {0}".format(t)
                    rem = True
                    tRemoved.append(t)
                    # The task is done processing.
                    with open(self.fNameOut, "at") as f:
                        print >> f, "{0}, {1}, {2}, {3}, {4}".format(t.tid, t.mo.idx, t.a, int(t.stTime), int(t.stTime) + int(t.dur) * CONST_SECINMILISEC)
            if rem :
                # Updating the state of the servers.
                sBef = len(m.tasks)
                m.tasks = [t for t in m.tasks if t.remDur > 0]


                if len(m.tasks) > 0:
                    ll = [t.reqs[CONST_LCPU] for t in m.tasks]
                    m.usages[CONST_LCPU] = sum(ll)
                else:
                    m.usages[CONST_LCPU] = 0.0
                sAft = len(m.tasks)
                removed += sBef - sAft


        self.lMachines =[m for m in self.lMachines if len(m.tasks)>0]
        if len(self.lMachines) ==0:
            self.lMachines =[Machine(0, 1.0, 1.0)]

        if verb:
            if removed > 0:
                print "\t{0} tasks removed in current bucket ".format(removed)
#             print "\033[92mRemoved {0} tasks\033[0m".format(removed)

        if verb:
            if tRemoved != []:
                for t in tRemoved:
                    print "\t\t {0}".format(t)
#         print "REM {0}".format(removed)
        return removed


    def cTimeInSec(self):
        return self.cTime / float(CONST_SECINMILISEC)

    def flush(self):
        return
        self.cTime = sys.maxint
        self.removeOldTasks(True)

    def printArrivingTasks(self,buf):
        print "[!{0}]-------------------------###".format(self.cTimeInSec() - self.bucketSize)
        print "{0} tasks arrive in bucket.".format(len(buf))
        for t in buf:
            print "\t\033[91m t {0} \033[0m".format(t)

    def printSolverAssignement(self,s,buf):
            print "\t\033[94m Solved in {0} ".format(round(s, 3))
            mu = set([t.mo for t in buf])

            print "\tAssigned to : {0}".format([m.idx for m in mu])
            for m in mu:
                print "\t== M{0} ==".format(m.idx)
                print "\t\tRunning {0} tasks".format(len(m.tasks))
                for t in m.tasks:
                    print "\t\t\t{0}".format(t)
                print "\t\tUsage {0}".format(m.usages[CONST_LCPU])
            print "\033[0m"
            print "###------------------------- [!{0}]".format(self.cTimeInSec()+ self.bucketSize)
            print

    def printDebugArrivingTasks(self,buf):
        print "[!{0}]-------------------------###".format(self.cTimeInSec() )
#         if(len(buf)>0):
#             print "\t{0} arrived tasks previous bucket.".format(len(buf))
#             for t in buf:
#                 print "\t\t {0} ".format(t)

    def printDebugSolverAssignement(self,s,buf):

            mu = set([t.mo for t in buf])
            if len(mu)>0:
                print "\ttasks will be hosted in next bucket (just arrived before):".format([m.idx for m in mu])
                for m in mu:
#                     print "\t\tM{0}".format(m.idx)
#                     print "\t\t Usage {0}".format(m.usages[CONST_LCPU])
                    for t in m.tasks:
                        print "\t\t{0}".format(t)


            #print "\tsolved in {0} ".format(round(s, 3))
            print "###------------------------- [!{0}]".format(self.cTimeInSec() + self.bucketSize)

            print



def start(dFiles, verb,nMachines, bucketSize, endObsWindow,solvName, ordering,ctsLim =None,CODE_ASSERT_HEU_WITH_CPLEX=False):
    lMachines = [Machine(i, 1.0, 1.0) for i in range(nMachines)]
    mon = Mon(dFiles, bucketSize, endObsWindow,lMachines)
    solver = heu(solvName, mon.bucketSize * 100, bucketSize, dFiles)
    st = time.clock()

    lastTaskLine = 0
    finished = 0

    maxBufSize = 0

    buf, lastTaskLine = mon.getNextTasks(lastTaskLine)
    maxBufSize = max(maxBufSize,len(buf))
    if verb: mon.printDebugArrivingTasks(buf)


    lb=mon.dumpLowerBound(verb)
    mon.dumpObjFunction(verb)

#     mon.updateRemTimes()
#     mon.removeOldTasks(verb)

    r, s = solver.solve(buf, lMachines, mon.cTime, ordering,CODE_ASSERT_HEU_WITH_CPLEX)
    mon.dumpTimings(verb, buf, s)


    if verb: mon.printDebugSolverAssignement(s,buf)

    #print mon.cTime, " <? ", mon.stTime+(mon.endObsWindow * CONST_SECINMILISEC)
    #print mon.nTasksSoFar



    while (mon.nTasksSoFar < mon.nLines and mon.cTime < mon.stTime+(mon.endObsWindow* CONST_SECINMILISEC)) or (mon.nTasksSoFar == mon.nLines and mon.cTime < mon.stTime+(mon.endObsWindow * CONST_SECINMILISEC)):

        if mon.nTasksSoFar < mon.nLines:
            buf, lastTaskLine = mon.getNextTasks(lastTaskLine)
        else:
            buf = []
            mon.nBuscketsSoFar += 1
            mon.cTime = mon.cTime + mon.bucketSize * CONST_SECINMILISEC

        if ctsLim!=None:
            if len(ctsLim)>0:
                if mon.cTime< ctsLim[0]:
                    continue
                if mon.cTime> ctsLim[1]:
                    break


        if verb : mon.printDebugArrivingTasks(buf)

        lb = mon.dumpLowerBound(verb)
        obj = mon.dumpObjFunction(verb)


        if lb>(obj+CONST_NUMIMPREC) :
    #       print "ERROR lb={0}>obj={1} at cTime={2}".format(lb,obj,mon.cTime)
            assert False," lb={0}>obj={1} at cTime={2}".format(lb,obj,mon.cTime)


        mon.updateRemTimes()
        mon.removeOldTasks(verb)

        # NOTE : Here is the place where heuristics can be called.
        if len(buf)>0:
            r, s = solver.solve(buf, mon.lMachines, mon.cTime, ordering, CODE_ASSERT_HEU_WITH_CPLEX)


        else:
            s=0


        mon.dumpTimings(verb, buf, s)


        if verb: mon.printDebugSolverAssignement(s,buf)


    # Flushing the buf.
    mon.flush()

    end = time.clock()

    print "{0}/{1} Seen {2} tasks in {3} buckets ({4}s). Solved in {5}s".format(solvName, ordering, solver.cumulTasks, mon.nBuscketsSoFar, mon.bucketSize, end - st)
    print "TotCost {0} seconds.".format(mon.totCost)
    print "LB {0} seconds".format(mon.LB)


def cleanFiles(fNames):
    for fName in fNames:
        with open(fName,"wt") as f:
            pass

'''

FMF_CPLEX/DDUR Seen 1570 tasks in 241 buckets (30s). Solved in 1.472698s
TotCost 78517 seconds.
LB 74360.0 seconds

FMF/DDUR Seen 1570 tasks in 241 buckets (30s). Solved in 0.401324s
TotCost 78518 seconds.
LB 74360.0 seconds

'''



if __name__ == '__main__' :

    givenSolv = None
    givenBSize = None
    givenErr = None
    givingOrdering = None
    givingEndObs = None

    if len(sys.argv) == 2:
        givenSolv =str(sys.argv[1])

    if len(sys.argv) == 3:
        givenErr =int(sys.argv[1])
        givenBSize = int(sys.argv[2])
        givingOrdering = CONST_O_LIST

    if len(sys.argv) == 4:
        givenSolv = str(sys.argv[1])
        givenErr =int(sys.argv[2])
        givenBSize = int(sys.argv[3])

    if len(sys.argv) == 5:
        givenSolv = str(sys.argv[1])
        givenErr =int(sys.argv[2])
        givenBSize = int(sys.argv[3])
        givingOrdering = str(sys.argv[4])

    if len(sys.argv) == 6:
        givenSolv = str(sys.argv[1])
        givenErr =int(sys.argv[2])
        givenBSize = int(sys.argv[3])
        givOrdering = str(sys.argv[4])
        givingEndObs = int(sys.argv[5])


    verb = False
    CODE_ASSERT_HEU_WITH_CPLEX = False
    nMachines = 1

    if givenBSize is None:
        bucketSizes = [2]
    else:
        bucketSizes=[givenBSize]


    if givenErr is None:
        instances = [0]
    else:
        if givenErr == 200:
            instances = [int(givenErr),int(givenErr)+50,int(givenErr)+100]
        else:
            instances = [int(givenErr),int(givenErr)+50]


    if givenSolv is None:
        solvers = [CONST_H_FMF]
    else:
        solvers =[givenSolv]

    if givingOrdering is None:
        orderings = [CONST_O_DDUR]
    else:
        orderings = [givingOrdering]

    if givingOrdering is None:
        endObsWindow =   3600
    else:
        endObsWindow = givenEndObs
    ctsLim = None


    baseIn = "../data/"
    baseOut = "../../results/uncertain/res"
    baseOutUsage = "../../results/uncertain/usage"
    baseOutLb = "../../results/uncertain/lb"
    baseOutTime = "../../results/uncertain/time"
    baseOutCplex = "../../results/uncertain/cplexStats"


    for ins in instances:
        fIn = "{0}allTasks_U{1}.csv".format(baseIn, ins)

        i = fIn.split("/")[-1].split(".")[0]

        for solvName in solvers:
            for ordering in orderings:
                for bucketSize in bucketSizes:

                    xp = "{0}_{1}_{2}_{3}".format(i, solvName, ordering, int(bucketSize))

                    dFiles = {
                        CONST_F_IN    : fIn,
                        CONST_F_SOL   : "{0}_{1}.csv".format(baseOut,         xp),
                        CONST_F_USAGE : "{0}_{1}.csv".format(baseOutUsage,    xp),
                        CONST_F_LB    : "{0}_{1}.csv".format(baseOutLb,       xp),
                        CONST_F_TIME  : "{0}_{1}.csv".format(baseOutTime,     xp),
                        CONST_F_CPLEX : "{0}_{1}.csv".format(baseOutCplex,    xp),
                        }
                    cleanFiles([dFiles[CONST_F_SOL],dFiles[CONST_F_USAGE],dFiles[CONST_F_LB],dFiles[CONST_F_TIME],dFiles[CONST_F_CPLEX]])

                    start(dFiles, verb, nMachines, bucketSize, (endObsWindow+bucketSize),solvName, ordering,ctsLim,CODE_ASSERT_HEU_WITH_CPLEX)
