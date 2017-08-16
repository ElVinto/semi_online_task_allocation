'''
Created on 22 Mar 2017

@author: varmant
'''

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

import time
import os
import sys
import subprocess

import threading
import logging

# This class should solve the cplex model model

class MySolverCplexThread(threading.Thread):
    def __init__(self, pbTxt, group=None, target=None, name=None, verbose=None,
                 ):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)

        self.setDaemon(True)
        self.pbTxt = pbTxt
        self.cplexStatus =None
        self.objCplex =None
        self.cplexTime =-1.0
        self.cplexMipRelativeGap =None
        self.cplexMipBestBound =None

        self.solCplex_idxLI_idxLM =[]

        return

    def run(self):
        runTime= time.clock()
        cmd = ['python ../heuristics/cplexProcess.py']

        self.process =  subprocess.Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True,universal_newlines=True)
        output = self.process.communicate(input=self.pbTxt.encode())[0]
        exitCode =self.process.returncode
        runTime = time.clock() - runTime
        if exitCode ==0:
            lines = output.split("\n")
            firstLine =True
            for l in lines:
                if l != '' :
                    if 'Exception'  not in l:
                        lvals = l.strip().split(",")
                        if firstLine:
                            self.cplexStatus = int(lvals[1])
                            self.objCplex = float(lvals[2])
                            self.cplexTime = (float(lvals[3])+runTime)
                            self.cplexMipRelativeGap = float(lvals[4])
                            self.cplexMipBestBound = float(lvals[5])
                            firstLine= False
                        else:
                            self.solCplex_idxLI_idxLM.append((int(lvals[0]),int(lvals[1])))
                    else:
                        self.cplexStatus = None
                        self.objCplex = None
                        self.cplexTime = -1.0
                        self.cplexMipRelativeGap =None
                        self.cplexMipBestBound = None
                        print output
        else:
            print output


        return

    def stop(self):
        if self.process is not None:
            print 'Stop solver'
            try:
                self.process.terminate()
            except Exception:
                print "Thread has already stopped"








def solve(heu,lMachines, lItems, cTime):

        solvingTimeHeu=time.clock()
        sol_idxLI_idxLM = []
        if heu.h == CONST_H_FMF_CPLEX:
            mbsd.solve(heu, lMachines, lItems, cTime,sol_idxLI_idxLM)
        if heu.h == CONST_H_myFF_CPLEX:
            myFF.solve(heu, lMachines, lItems, cTime,sol_idxLI_idxLM)
        elif heu.h == CONST_H_myBFD_CPLEX:
            myBF.solve(heu, lMachines, lItems, cTime, sol_idxLI_idxLM,crit=CONST_H_myBFD)
        elif heu.h == CONST_H_myBFR_CPLEX:
            myBF.solve(heu, lMachines, lItems, cTime, sol_idxLI_idxLM,crit=CONST_H_myBFR)
        if heu.h == CONST_H_myNF_CPLEX:
            myNF.solve(heu, lMachines, lItems, cTime,sol_idxLI_idxLM)
        if heu.h == CONST_H_myHA_CPLEX:
            myHA.solve(heu, lMachines, lItems, cTime,sol_idxLI_idxLM)
        elif heu.h == CONST_H_myMRD_CPLEX:
            myMR.solve(heu, lMachines, lItems, cTime, sol_idxLI_idxLM,crit=CONST_H_myMRD)
        elif heu.h == CONST_H_myMRR_CPLEX:
            myMR.solve(heu, lMachines, lItems, cTime, sol_idxLI_idxLM,crit=CONST_H_myMRR)
        if heu.h == CONST_H_mySS_CPLEX:
            mySS.solve(heu, lMachines, lItems, cTime,sol_idxLI_idxLM)

        solvingTimeHeu=time.clock() -solvingTimeHeu

        solvingTimeCplex=time.clock()

        objHeu , sol_dur_idxLM = heu.getRunTimeOfAllocatedMachinesInSolution(lMachines, lItems,sol_idxLI_idxLM)

        remSolvingTime = max(0.5,(requestSolvTime(heu.bucketSize)-solvingTimeHeu)) # add .5 to cplex in case there is no time

#         pbFName = str(heu.dFiles[CONST_F_TMP]).replace(".csv", "_pb.txt")
        pbTxt =createPb(heu,lMachines, lItems,sol_idxLI_idxLM,sol_dur_idxLM,objHeu,remSolvingTime,cTime)

        cplexThread = MySolverCplexThread(pbTxt)
        cplexThread.start()

#         print "remSolvingTime",remSolvingTime
        cplexThread.join(remSolvingTime+1.0) # let 1.0 to cplex to stop properly
        if cplexThread.isAlive():
            cplexThread.stop()

        if cplexThread.objCplex != None:
            if objHeu>cplexThread.objCplex:
                sol_idxLI_idxLM = cplexThread.solCplex_idxLI_idxLM

        if cplexThread.cplexTime == -1.0:
            cplexThread.cplexTime =heu.bucketSize

        solvingTimeCplex=time.clock()-solvingTimeCplex+cplexThread.cplexTime

        with open(heu.dFiles[CONST_F_CPLEX], "at") as statFName:
            print >> statFName, "{0},{1},{2},{3},{4},{5},{6},{7},{8},{9}".format(cTime, len(lMachines),len(lItems)
                                                                         , objHeu , solvingTimeHeu
                                                                         , cplexThread.cplexStatus, cplexThread.objCplex,solvingTimeCplex,cplexThread.cplexMipRelativeGap,cplexThread.cplexMipBestBound)

        checkSolution(cTime,lMachines, lItems,sol_idxLI_idxLM)

        heu.assignSolution(lItems,lMachines, sol_idxLI_idxLM,cTime)

        return solvingTimeHeu + solvingTimeCplex

def requestSolvTime(bucketSize):
    if bucketSize ==2:
        return 1.5
    if bucketSize ==10:
        return 8.0
    if bucketSize ==20:
        return 18.0
    if bucketSize ==30:
        return 28.0

    return bucketSize


def createPb(heu,lMachines, lItems,sol_idxLI_idxLM,sol_dur_idxLM,sol_obj,remSolvingTime,cTime):
    pb=''
#     with open(pbFName,"wt") as f:

#         print >> f, "#LMachines: idxLMachine,remainingCapacity,longestEstimatedRemainingTime"
    pb+="#LMachines: idxLMachine,remainingCapacity,longestEstimatedRemainingTime"+"\n"
    for j in range(len(lMachines)):
        remCap = lMachines[j].capacities[CONST_LCPU] - lMachines[j].usages[CONST_LCPU]
#             print >> f, str(j)+','+ str(remCap)+','+ str(lMachines[j].lrt)
        pb+=str(j)+','+ str(remCap)+','+ str(lMachines[j].lrt)+"\n"

#         print >> f, "#LItems: idxLItems,cpu,estimatedDuration"
    pb+="#LItems: idxLItems,cpu,estimatedDuration"+"\n"
    for i in range(len(lItems)):
#             print >> f,str(i)+','+str(lItems[i].reqs[CONST_LCPU])+','+str(lItems[i].remEstDur)
        pb+=str(i)+','+str(lItems[i].reqs[CONST_LCPU])+','+str(lItems[i].remEstDur)+"\n"

#         print >> f, "#Incubent: idxLItems,idxLMachine"
    pb+="#Incubent: idxLItems,idxLMachine"+"\n"
    for (i,j) in sol_idxLI_idxLM:
#             print >> f,str(i)+','+str(j)
        pb+=str(i)+','+str(j)+"\n"

#         print >> f, "#ExtraIncubent: longestEstimatedRemainingTime,idxLMachine"
    pb+="#ExtraIncubent: longestEstimatedRemainingTime,idxLMachine"+"\n"
    for (dur,j) in sol_dur_idxLM:
#             print >> f,str(dur)+','+str(j)
        pb+=str(dur)+','+str(j)+"\n"

#         print >> f, "#OtherParams: ObjectiveIncubent,SolvingTime,StatFName,cTime,bucketSize"
    pb+="#OtherParams: ObjectiveIncubent,SolvingTime,StatFName,cTime,bucketSize"+"\n"
#         print >> f,str(sol_obj)+','+str(remSolvingTime)+','+heu.dFiles[CONST_F_CPLEX]+','+str(cTime)+','+str(heu.bucketSize)
    pb+=str(sol_obj)+','+str(remSolvingTime)+','+str(cTime)+','+str(heu.bucketSize)+"\n"
    return pb


def checkSolution(cTime, lMachines, lItems, sol_idxLI_idxLM):

    for i in range(len(lItems)):
        nbAssignedMachines=0
        for (k,j) in sol_idxLI_idxLM:
            if k==i:
                nbAssignedMachines+=1
        assert nbAssignedMachines == 1, "cTime:{0} {1} is assigned to {2} machines".format(cTime, i,nbAssignedMachines)


    for j in range(len(lMachines)):
        nvMachineUsage = lMachines[j].usages[CONST_LCPU]
        for (i,k) in sol_idxLI_idxLM:
            if k==j:
                nvMachineUsage += lItems[i].reqs[CONST_LCPU]
        assert nvMachineUsage <=  (lMachines[j].capacities[CONST_LCPU]+ CONST_NUMIMPREC), "cTime:{0} nvMachineUsage:{1} capacity{2}".format(cTime, nvMachineUsage,(lMachines[j].capacities[CONST_LCPU]+ CONST_NUMIMPREC))



def erasePb(fName):
    with open(fName,"wt") as f:
        print >> f, ""


