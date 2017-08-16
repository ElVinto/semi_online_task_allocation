import operator
from const import *
from utils import *

from collections import OrderedDict
import mergeBinsByDuration as  mbd
import mergeBinsSeqByDuration as  mbsd
import mergeBinsSeqByStartTime as mbsbST
import myFirstFit as myFF
import myNextFit as myNF
import myBestFit as myBF

import mySumOfSquares as mySS
import myMaxRest as myMR
import myHarm as myHA
import myWorseFit as myWF

import cplexHeuristics as cplxHeu

import time
import os

import sys

import cplex
from cplex._internal._constants import CPX_PARAM_EPGAP, CPX_PARAM_TILIM, CPX_STAT_OPTIMAL, CPXMIP_OPTIMAL, CPX_PARAM_ADVIND,CPX_PARAM_RINSHEUR
from cplex.callbacks import MIPInfoCallback

"""
A heuristic should implement the following elements.
- A decision heuristic assigning all tasks to machines without breaking the capacity constraint.
- A mechanism to kill the heuristics if it take more than the cut off time.
- Should perform the actual assignment in the machine and task objects.
"""

class heu(object):

    def __init__(self, h, tCutOff, bucketSize, dFiles):
        self.h = h
        self.tCutOff = tCutOff
        self.tStart = None
        self.cumulTasks = 0
        self.bucketSize = bucketSize
        self.fCplex = dFiles[CONST_F_CPLEX]
        self.dFiles = dFiles

    def assign(self, m, t, cTime):
        t.stTime = cTime  + (self.bucketSize * CONST_SECINMILISEC)  # Track the starting time
        t.mo = m            # Keep a ref to the machine in the task
        m.tasks.append(t)   # Keep a ref to the task in the machine
        # UPdate the usage within the machine
        m.usages[CONST_LCPU] += t.reqs[CONST_LCPU]
        self.cumulTasks += 1
        m.lrt = max(m.lrt, t.remEstDur+ self.bucketSize)

        assert(m.usages[CONST_LCPU] <= m.capacities[CONST_LCPU] +CONST_NUMIMPREC), "MachineIdx {0} at {1} overloaded usage:{2:.15f} capa:{3:.15f}".format(m.idx,cTime,m.usages[CONST_LCPU],m.capacities[CONST_LCPU])


    def assignSolution(self,lItems, lMachines,sol_idxLI_idxLM,cTime):
        for (i,j) in sol_idxLI_idxLM:
            self.assign(lMachines[j],lItems[i],cTime)

    def solve(self, lItems, lMachines, cTime, ordering,CODE_ASSERT_HEU_WITH_CPLEX):

        self.tStart = time.clock()

        # heuristics that need an extra number of empty machines
        if self.h in [ CONST_H_CPLEX , CONST_H_FF , CONST_H_BFR ,CONST_H_BFRTD, CONST_H_BFD, CONST_H_NF]:
            self.addNewMachinesIfNeeded(lMachines,lItems)


        if self.h not in [CONST_H_FMF, CONST_H_FMF_CPLEX]:
            lMachines.sort(key = lambda m:m.lrt, reverse = True)
            if ordering != None: lItems = orderLTasks(lItems, ordering)

        if self.h == CONST_H_CPLEX:
            retVal = self.cplex(lMachines, lItems, cTime)
        elif self.h == CONST_H_FF:
            retVal = self.firstFit(lMachines, lItems, cTime)
        elif self.h == CONST_H_NF:
            self.mPtr = 0
            retVal = self.nextFit(lMachines, lItems, cTime)
        elif self.h == CONST_H_BFR:
            retVal = self.bestFit(lMachines, lItems, cTime,  crit = CONST_H_BFR)
        elif self.h == CONST_H_BFD:
            retVal = self.bestFit(lMachines, lItems, cTime, crit = CONST_H_BFD)
        elif self.h == CONST_H_BFRTD:
            retVal = self.bestFit(lMachines, lItems, cTime, crit = CONST_H_BFRTD)
        elif self.h == CONST_H_FMF:
            t = mbsd.solve(self, lMachines, lItems, cTime)
        elif self.h == CONST_H_myFF:
            t = myFF.solve(self, lMachines, lItems, cTime)
        elif self.h == CONST_H_myNF:
            t = myNF.solve(self, lMachines, lItems, cTime)
        elif self.h == CONST_H_myBFD:
            t = myBF.solve(self, lMachines, lItems, cTime, crit=CONST_H_myBFD)
        elif self.h == CONST_H_myBFR:
            t = myBF.solve(self, lMachines, lItems, cTime, crit=CONST_H_myBFR)
        elif self.h == CONST_H_myMRD:
            t = myMR.solve(self, lMachines, lItems, cTime,crit=CONST_H_myMRD)
        elif self.h == CONST_H_myMRR:
            t = myMR.solve(self, lMachines, lItems, cTime,crit=CONST_H_myMRR)
        elif self.h == CONST_H_myHA:
            t = myHA.solve(self, lMachines, lItems, cTime)
        elif self.h == CONST_H_mySS:
            t = mySS.solve(self, lMachines, lItems, cTime)
        elif self.h in  [CONST_H_FMF_CPLEX,CONST_H_myFF_CPLEX,CONST_H_myBFD_CPLEX,CONST_H_myBFR_CPLEX,CONST_H_myNF_CPLEX,CONST_H_myMRR_CPLEX,CONST_H_myMRD_CPLEX,CONST_H_myHA_CPLEX,CONST_H_mySS_CPLEX]:
            t = cplxHeu.solve( self,lMachines, lItems, cTime)


        else: assert(False), "Heuristic not implemented"

        stime = time.clock() - self.tStart

        if self.h in  [CONST_H_FMF_CPLEX,CONST_H_myFF_CPLEX,CONST_H_myBFD_CPLEX,CONST_H_myBFR_CPLEX,CONST_H_myNF_CPLEX,CONST_H_myMRR_CPLEX,CONST_H_myMRD_CPLEX,CONST_H_myHA_CPLEX,CONST_H_mySS_CPLEX]:
            stime = t

        if stime > self.bucketSize:
            print "{2} - Too long : {0} on {1}".format(stime, len(lItems), self.h)

        return True, stime

    def addNewMachinesIfNeeded(self,lMachines,lItems):

#         if(len(lItems)<=0):
#             return 0
#
#         for i in range(len(lItems)+1):
#             idx = lMachines[-1].idx+1
#             lMachines.append(Machine(idx, 1.0, 1.0))
#         return len(lItems)+1

        defaultMachineCPUCapacity =1.0
        maxIdxM = max(m.idx for m in lMachines)

        ub2 = 1
        resourceAllocToCurrentMachine = lItems[0].reqs["cpu"]
        for i in range(1, len(lItems)):
            t = lItems[i]
            resourceAllocToCurrentMachine += t.reqs["cpu"]
#             print " resAlloc ",  resourceAllocToCurrentMachine
            if resourceAllocToCurrentMachine>defaultMachineCPUCapacity:
                ub2+=1
#                 print " ub2+=1 ",  ub2
                resourceAllocToCurrentMachine=  t.reqs["cpu"]

        for i in range(ub2):
            maxIdxM +=1
            lMachines.append(Machine(maxIdxM, 1.0, 1.0))
#             print "creating machine ", idx

        return ub2

    def firstFit(self, lMachines, lItems, cTime):

        for i in lItems:
            for m in lMachines:

                tc = time.clock()

                if self.tCutOff <= tc - self.tStart:
                    return False

                post = i.reqs[CONST_LCPU] + m.usages[CONST_LCPU]

                if post <= m.capacities[CONST_LCPU]:
                    # Space enough. Assign.
                    self.assign(m, i, cTime)
                    #self.cumulTasks += 1
                    break

            if i.mo == None: assert(False), "Could not assign"
        return True

    def nextFit(self, lMachines, lItems, cTime):
        """

        """
        #print "DEBUG"
        m = lMachines[self.mPtr]

        for i in lItems:

            tc = time.clock()

            if self.tCutOff <= tc - self.tStart:
                return False

            post = m.usages[CONST_LCPU] + i.reqs[CONST_LCPU]

            while post > m.capacities[CONST_LCPU]:
                    self.mPtr += 1
                    if self.mPtr >= len(lMachines) - 1: self.mPtr = 0
                    m = lMachines[self.mPtr]
                    post = m.usages[CONST_LCPU] + i.reqs[CONST_LCPU]

            # Found a machine. Can stop here.

            self.assign(m, i, cTime)
            if i.mo == None: assert(False), "Could not assign"
            #self.cumulTasks += 1

        return True

    def bestFit(self, lMachines, lItems, cTime, crit = CONST_H_BFR):
        # This implements best fit heuristic
        # Three variants are considered here.
        # Best fit on reqs (bp style), on durations or on duration * reqs

        for i in lItems:

            rc = {}

            for m in lMachines:

                tc = time.clock()

                if self.tCutOff <= tc - self.tStart:
                    return False

                post = i.reqs[CONST_LCPU] + m.usages[CONST_LCPU]

                if post <= m.capacities[CONST_LCPU]:
                    if crit == CONST_H_BFR:
                        # Best fit on the requirements.
                        rc[m] = m.capacities[CONST_LCPU] - post
                        #print m.idx, " -> ", rc[m]
                        if rc[m] == 0.0:
                            # Completely filing the machine : break
                            break
                        if post == i.reqs[CONST_LCPU]:
                            # Adding to nex machine
                            break

                    elif crit == CONST_H_BFD:
                        # This measures the distance in terms of durations
                        rc[m] = float(abs(m.lrt - i.remEstDur))
                        if rc[m] < 1.0:
                            # Mathing an other one
                            break
                        if m.lrt == 0.0:
                            # Considering new machine : break
                            break


            # This is very inefficient.
            #print rc
            bfm = min(rc, key=rc.get)
            #print "item {0} chosen -> ".format(i.tid), bfm.idx
            # Assigning
            self.assign(bfm, i, cTime)
            #self.cumulTasks += 1

            if i.mo == None: assert(False), "Failed to assign"

        # Sorting the list of machines here.
        return True

    def getRunTimeOfAllocatedMachinesInSolution(self,lMachines, lItems,sol_idxLI_idxLM):
        sol_dur_idxLM =[]
        obj =0
#         print "ExtraIncubent"
        mInSol = set([idxLM for(idxI,idxLM) in sol_idxLI_idxLM])

        # max estimated duration of machines assigned in Solution
#         print " In Solution"
        for idxLM in mInSol:
            maxEstDurM = 0
            # max estimated duration of tasks assigned in Solution
            for(idxI,idxMb) in sol_idxLI_idxLM:
                if(idxLM==idxMb):
                    if(lItems[idxI].remEstDur>maxEstDurM):
                        maxEstDurM = lItems[idxI].remEstDur
            # max estimated duration of running tasks
            for t in lMachines[idxLM].tasks:
                if t.remEstDur >maxEstDurM:
                    maxEstDurM = t.remEstDur

#             print "  dur(e_{1}) == {0}".format(maxEstDurM, idxLM)
            sol_dur_idxLM.append((maxEstDurM,idxLM))
            obj+= maxEstDurM

        # max estimated duration of machines not assigned in Solution
#         print " Previously Assigned"
        for idxLM in range(len(lMachines)):
            if idxLM not in mInSol:
                maxEstDurM = 0
                for t in lMachines[idxLM].tasks:
                    if t.remEstDur >maxEstDurM:
                        maxEstDurM = t.remEstDur

#                 print "  dur(e_{1}) == {0}".format(maxEstDurM, idxLM)
                sol_dur_idxLM.append((maxEstDurM,idxLM))
                obj+= maxEstDurM

        return obj ,sol_dur_idxLM


    def heu_CPLEX(self,lMachines, lItems, cTime,CODE_ASSERT_HEU_WITH_CPLEX):

        solvingTimeHeu=0
        sol_idxLI_idxLM = []
        if self.h == CONST_H_FMF_CPLEX:
            solvingTimeHeu = mbsd.solve(self, lMachines, lItems, cTime,sol_idxLI_idxLM)
        if self.h == CONST_H_myFF_CPLEX:
            solvingTimeHeu = myFF.solve(self, lMachines, lItems, cTime,sol_idxLI_idxLM)
        elif self.h == CONST_H_myBFD_CPLEX:
            solvingTimeHeu = myBF.solve(self, lMachines, lItems, cTime, sol_idxLI_idxLM,crit=CONST_H_myBFD)
        elif self.h == CONST_H_myBFR_CPLEX:
            solvingTimeHeu = myBF.solve(self, lMachines, lItems, cTime, sol_idxLI_idxLM,crit=CONST_H_myBFR)
        if self.h == CONST_H_myNF_CPLEX:
            solvingTimeHeu = myNF.solve(self, lMachines, lItems, cTime,sol_idxLI_idxLM)
        if self.h == CONST_H_myHA_CPLEX:
            solvingTimeHeu = myHA.solve(self, lMachines, lItems, cTime,sol_idxLI_idxLM)
        elif self.h == CONST_H_myMRD_CPLEX:
            solvingTimeHeu = myMR.solve(self, lMachines, lItems, cTime, sol_idxLI_idxLM,crit=CONST_H_myMRD)
        elif self.h == CONST_H_myMRR_CPLEX:
            solvingTimeHeu = myMR.solve(self, lMachines, lItems, cTime, sol_idxLI_idxLM,crit=CONST_H_myMRR)
        if self.h == CONST_H_mySS_CPLEX:
            solvingTimeHeu = mySS.solve(self, lMachines, lItems, cTime,sol_idxLI_idxLM)

        objHeu , sol_dur_idxLM = self.getRunTimeOfAllocatedMachinesInSolution(lMachines, lItems,sol_idxLI_idxLM)

#         print " inc:{0} ".format(sol_idxLI_idxLM)
#         for i,t in enumerate(lItems):
#             print " {0}: {1}".format(i,t)

#         if CODE_ASSERT_HEU_WITH_CPLEX:
        assert len(sol_idxLI_idxLM) == len(lItems),"len(sol):{0}, len(lItems):{1}".format(len(sol_idxLI_idxLM),len(lItems))

        for m in lMachines:
            nv_usage = m.usages[CONST_LCPU]
            for (idxLI, idxLM) in sol_idxLI_idxLM:
                if m == lMachines[idxLM]:
                    nv_usage+=lItems[idxLI].reqs[CONST_LCPU]
            if nv_usage > 1.0 :
                assert False, "Overloaded Machine in Solution"+str(nv_usage)+str(m)

#         print "obj: ",objHeu,"sol_idxLI_idxLM: ",sol_idxLI_idxLM

        solvingTimeCplex = time.clock()

        objCplex = self.cplex(lMachines, lItems, cTime, self.bucketSize-solvingTimeHeu, sol_idxLI_idxLM,sol_dur_idxLM,objHeu,CODE_ASSERT_HEU_WITH_CPLEX)

        solvingTimeCplex = time.clock() - solvingTimeCplex


        return solvingTimeHeu+solvingTimeCplex



# if __name__ == '__main__':
#
#
#     benchs = ["googleRand"]
#
#     for b in benchs:
#         for inst in os.listdir("../data/{0}/".format(b)):
#             if inst.endswith(".csv"):
#
#                 iNum = int(inst.split("_")[2].split(".")[0])
#                 if iNum != 5: continue
#
#                 if b == "integerInstances":
#                     lItems = parseInstance("../data/{0}/{1}".format(b, inst), floats = False)
#                     lMachines = [Machine(i + 1, 100, 100) for i in range(len(lItems))]
#                     cap = 100
#                 else:
#                     lItems = parseInstance("../data/{0}/{1}".format(b, inst), floats = True)
#                     lMachines = [Machine(i + 1, 0.5, 0.5) for i in range(len(lItems))]
#                     cap = 0.5
#
#                 st = time.clock()
#
#                 lMachinesub = lMachines[:]
#                 lItemsub = lItems[:]
#                 lb = lb_4(lItems, lMachines, cap)
#                 solver = heu(CONST_H_FF, 600.0)
#                 lItemsub = orderLTasks(lItemsub, CONST_O_DDUR)
#                 ub = solver.solve(lItemsub, lMachinesub)
#
#                 #outFile = "../../results/{0}/lbs/lbs.csv".format(b)
#                 #with open(outFile, "at") as of:
#                     #print >> of, "{0}, {1}, {2}, {3}".format(len(lItems), iNum, lb, time.clock() - st)
#                 #print "{0}, {1}, {2}, {3}".format(len(lItems), iNum, lb, time.clock() - st)
#                 #print "{0}, {1}".format(len(lItems), iNum)
#
#                 ub = getObjValue(lItemsub, lMachinesub)
#                 if ub == lb:
#                     tok = "Closed"
#                 if ub > lb:
#                     tok = "Open"
#                 if ub < lb:
#                     tok = "Problem"
#
#                 print "{0}, {1}, {2}, {3}, {4}".format(len(lItems), iNum, lb, ub, tok)
