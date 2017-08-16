'''
Created on 31 Mar 2017

@author: varmant
'''


import time
import os

import threading
import logging

import sys
import cplex
from cplex._internal._constants import CPX_PARAM_EPGAP, CPX_PARAM_ADVIND, CPX_PARAM_HEURFREQ, CPX_PARAM_RINSHEUR, CPXMIP_OPTIMAL,CPXMIP_OPTIMAL_TOL,CPXMIP_NODE_LIM_FEAS,CPXMIP_TIME_LIM_FEAS,CPXMIP_FAIL_FEAS,CPXMIP_MEM_LIM_FEAS,CPXMIP_ABORT_FEAS
from cplex.callbacks import MIPInfoCallback

import operator
import fileinput
import subprocess
from const import *
from utils import *


class CplexProcess(object):

    def __init__(self, fileIn):

        self.input =fileIn

        self.lMachinesIdx = []
        self.lMachinesRemCapa = []
        self.lMachinesLRT = []

        self.lItemsIdx = []
        self.lItemsCpuReq = []
        self.lItemsRemEstTime = []

        self.incubent =[]
        self.extraIncubent =[]

        self.objIncubent =None
        self.timeLimit =None

        self.totalTime = time.clock()
        self.parsePb()



    def parsePb(self):

        inLMachines =False
        inLItems = False
        inIncubent =False
        inExtraIncubent=False
        inOtherParams = False

        for l in self.input:


            if  "#LMachines" in l:
                inLMachines = True
                continue
            if  "#LItems" in l :
                inLItems = True
                inLMachines =False
                continue
            if  "#Incubent" in l:
                inIncubent = True
                inLItems = False
                continue
            if  "#ExtraIncubent" in l :
                inExtraIncubent = True
                inIncubent =False
                continue
            if  "#OtherParams" in l : # ObjIncubent,SolvingTime,StatFName,cTime,bucketSize
                inOtherParams =True
                inExtraIncubent = False
                continue

            if inLMachines :
                lVals=l.strip().split(',')
                idxLM = int(lVals[0])
                remCapacity = float(lVals[1])
                remLonguestRemEstTime = float(lVals[2])

                self.lMachinesIdx.append(idxLM)
                self.lMachinesRemCapa.append(remCapacity)
                self.lMachinesLRT.append(remLonguestRemEstTime)

            if inLItems :
                lVals=l.strip().split(',')
                idxLI = int(lVals[0])
                cpuReq = float(lVals[1])
                remEstTime = float(lVals[2])

                self.lItemsIdx.append(idxLI)
                self.lItemsCpuReq.append(cpuReq)
                self.lItemsRemEstTime.append(remEstTime)

            if inIncubent :
                lVals=l.strip().split(',')
                i = int(lVals[0])
                j = int(lVals[1])
                self.incubent.append((i,j))

            if inExtraIncubent :
                lVals=l.strip().split(',')
                dur = float(lVals[0])
                j = int(lVals[1])
                self.extraIncubent.append((dur,j))

            if inOtherParams :
                lVals=l.strip().split(',')
                self.objIncubent = float(lVals[0])
                self.timeLimit = float(lVals[1])
                self.cTime = int(lVals[2])
                self.bucketSize = int(lVals[3])
                break


    def solvePb(self):

        nItems = len(self.lItemsCpuReq)
        nBins = len(self.lMachinesLRT)


        c = cplex.Cplex()
        c.set_log_stream(None)
        c.set_error_stream(None)
        c.set_warning_stream(None)
        c.set_results_stream(None)
        #c.parameters.mip.strategy.probe.set(3)
        c.parameters._set(CPX_PARAM_EPGAP, .0)
        c.parameters._set(CPX_PARAM_ADVIND, 2)
        c.parameters._set(CPX_PARAM_HEURFREQ,0)
        c.parameters._set(CPX_PARAM_RINSHEUR, 0)

        c.parameters.timelimit.set(self.timeLimit)

        # Set threads to 1
        c.parameters.threads.set(1)


        #c.parameters.mip.limits.nodes.set(10000000)

        x = [] # Two dim var array nItems * nBins
        e = [] # end run time


        c.objective.set_sense(c.objective.sense.minimize)

        # x_ij = 1 mean that item i is assign to machine j.
        # Otherwise
        for i in range(nItems):
            x.append([])
            for j in range(nBins):
                x[i].append("x_" + str(i) + "_" + str(j))

        allx = [item for sublist in x for item in sublist]
        c.variables.add(names = allx, types = ["B"] * (nBins * nItems))
#         print "allx:{0}".format(allx)

        # e_j encodes the max run time on a machine
        lbs = []
        ubs = []
        longestTask = max(self.lItemsRemEstTime)

        for j in range(nBins):
            lbs.append(int(self.lMachinesLRT[j]))
            ubs.append(max(longestTask, int(self.lMachinesLRT[j])))
            e.append("e_" + str(j))

        c.variables.add(obj = [1]*nBins, names = e, lb = lbs, ub = ubs, types = [c.variables.type.integer] * nBins) # the max duration are int values


        # For all items : Assignment constraint
        for i in range(nItems):
            vrs = [x[i][j] for j in range(nBins)]
            cts = [1] * nBins
            c.linear_constraints.add(lin_expr = [cplex.SparsePair(vrs, cts)], senses = ["E"], rhs = [1])

        ## Load constraint for each machine
        # The sum of the cpu requirements of the tasks assigned to a machine is lower than the machine capacity
        for j in range(nBins):
            # forall j, sum_i x_ij * cpu_i <= capa_j- usage_j
            vrs = [x[i][j] for i in range(nItems)]
            cts = self.lItemsCpuReq
            remCap = self.lMachinesRemCapa[j]

            c.linear_constraints.add(lin_expr = [cplex.SparsePair(vrs, cts)], senses = ["L"], rhs = [remCap])


        # Write constraint on machine duration e_j
        for j in range(nBins):
            # 0 <= e_j - x_ij * remEstDur_i
            for i in range(nItems):
                vrs = [e[j],x[i][j]]
                cts = [1,-self.lItemsRemEstTime[i]]
                c.linear_constraints.add(lin_expr = [cplex.SparsePair(vrs, cts)], senses = ["G"], rhs = [0])

            # The incumbent is a set of sparse pairs


#             print "incubent {0} ".format(incubent)
#             print "nBins {0} nItems {1}".format(nBins,nItems)
#             print "x: {0}".format(x)
        if  self.incubent is not None:
            all_vars = []
            all_vals = []
            # Set all x[i][j] variables
            for j in range(nBins):

                # map the value xij in incubent to one
                vars_xij_1 = [x[i][j] for i in range(nItems) if (i, j) in self.incubent]
                if len(vars_xij_1)>0:
                    all_vars.extend(vars_xij_1)
                    all_vals.extend([1] * len(vars_xij_1))

                # map the value of xij not in incumbent to zero
                vars_xij_0 = [x[i][j] for i in range(nItems) if (i, j) not in self.incubent]
                if len(vars_xij_0)>0:
                    all_vars.extend(vars_xij_0)
                    all_vals.extend([0] * len(vars_xij_0))


            # Set all e[j]  variable
            lIdxM = [k[1] for k in self.extraIncubent]
#             print "lIdxM:", lIdxM
            vars_e_d = [e[j] for j in lIdxM]
#             print "vrs_e!=0 : ", vrs_e
            vals_e_d = [k[0] for k in self.extraIncubent]
#             print "vals_e: ", vals_e
            if len(vars_e_d)>0:
                all_vars.extend(vars_e_d)
                all_vals.extend(vals_e_d)

            # Set the value to unassigned machine
            vars_e_0 = [e[j] for j in range(nBins) if j not in lIdxM ]
            vals_e_0 = [0]*len(vars_e_0)
#             print "vrs_e=0 : ", vrs_e
            if len(vars_e_0)>0:
                all_vars.extend(vars_e_0)
                all_vals.extend(vals_e_0)

            # Optional CUT   sum_j(e_j) <= obj(heu)
            if(len(e)>0):
                c.linear_constraints.add(lin_expr = [cplex.SparsePair(e, [1]*len(e))], senses = ["L"], rhs = [self.objIncubent])

            # adding the incubent as a start solution to cplex
            if len(all_vars)>0:
                c.MIP_starts.add(cplex.SparsePair(ind = all_vars, val = all_vals ), c.MIP_starts.effort_level.check_feasibility, "Heu")

#         c.write("debug.lp")

        c.solve()


        self.totalTime = time.clock()-self.totalTime

        if c.solution.get_status() in [CPXMIP_OPTIMAL,  CPXMIP_OPTIMAL_TOL,CPXMIP_NODE_LIM_FEAS,CPXMIP_TIME_LIM_FEAS,CPXMIP_FAIL_FEAS,CPXMIP_MEM_LIM_FEAS,CPXMIP_ABORT_FEAS ]:
            try:
                print "#Solution,"+str(c.solution.get_status())+","+str(c.solution.get_objective_value())+","+str(self.totalTime)+","+str(c.solution.MIP.get_mip_relative_gap())+","+str(c.solution.MIP.get_best_objective())
                for i in range(nItems):
                    nbMachineAssignedToItem =0
                    for j in range(nBins):
                        if round(c.solution.get_values(x[i][j])) == 1.0 :
                            print "{0},{1}".format(i,j)
                            nbMachineAssignedToItem+=1
                    if  nbMachineAssignedToItem<0 or nbMachineAssignedToItem>1 :
                        assert False," item not or over  assigned in Solution idx:"+ str(i)

            except Exception as excpt:
                print 'Exception: ',excpt





if __name__ == '__main__' :

    p = CplexProcess(fileinput.input())
    p.solvePb()




