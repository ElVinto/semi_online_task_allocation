'''
Created on 2 Apr 2017

@author: varmant
'''
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

import cplex
from cplex._internal._constants import CPX_PARAM_EPGAP, CPX_PARAM_TILIM, CPX_STAT_OPTIMAL, CPXMIP_OPTIMAL, CPX_PARAM_ADVIND,CPX_PARAM_RINSHEUR
from cplex.callbacks import MIPInfoCallback



def cplex(self, lMachines, lItems,  incubent = None, extraIncubent=None, objIncubent =None):


    nItems = len(lItems)
    nBins = len(lMachines)


    c = cplex.Cplex()
    c.set_log_stream(None)
    c.set_error_stream(None)
    c.set_warning_stream(None)
    c.set_results_stream(None)

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
    longestTask = max([i.remEstDur for i in lItems])

    for j in range(nBins):

        maxRemEstDur = lMachines[j].lrt

        lbs.append(int(maxRemEstDur))
        ubs.append(max(longestTask, int(maxRemEstDur)))
        e.append("e_" + str(j))
    caps = [m.capacities[CONST_LCPU] for m in lMachines]
    #         c.variables.add(obj = caps, names = e, lb = lbs, ub = ubs, types = [c.variables.type.continuous] * nBins) # Faster but can be less Quality
    c.variables.add(obj = caps, names = e, lb = lbs, ub = ubs, types = [c.variables.type.integer] * nBins) # the max duration are int values


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
        cts = [lItems[i].reqs[CONST_LCPU] for i in range(nItems)]
        remCap = lMachines[j].capacities[CONST_LCPU] - lMachines[j].usages[CONST_LCPU]

        c.linear_constraints.add(lin_expr = [cplex.SparsePair(vrs, cts)], senses = ["L"], rhs = [remCap])

    #             if cTime == 1222000000:
    #                 print vrs," <= ",remCap
    #                 print cts," <= ",remCap


    # Write constraint on machine duration e_j
    for j in range(nBins):
        # 0 <= e_j - x_ij * remEstDur_i
        for i in range(nItems):
            vrs = [e[j],x[i][j]]
            cts = [1,-lItems[i].remEstDur ]
            c.linear_constraints.add(lin_expr = [cplex.SparsePair(vrs, cts)], senses = ["G"], rhs = [0])



    if  incubent is not None:

        all_vars = []
        all_vals = []
        # Set all x[i][j] variables
        for j in range(nBins):

            # map the value xij in incubent to one
            vars_xij_1 = [x[i][j] for i in range(nItems) if (i, j) in incubent]
            if len(vars_xij_1)>0:
                all_vars.extend(vars_xij_1)
                all_vals.extend([1] * len(vars_xij_1))

            # map the value of xij not in incumbent to zero
            vars_xij_0 = [x[i][j] for i in range(nItems) if (i, j) not in incubent]
            if len(vars_xij_0)>0:
                all_vars.extend(vars_xij_0)
                all_vals.extend([0] * len(vars_xij_0))


            # Forcing Incubent assignement:  forall xij, xij= e_(incubent[j]) "
            for (i,j) in incubent:
                c.linear_constraints.add(lin_expr = [cplex.SparsePair([x[i][j]], [1])], senses = ["E"], rhs = [1])



        # Set all e[j]  variable
        lIdxM = [k[1] for k in extraIncubent]
    #             print "lIdxM:", lIdxM
        vars_e_d = [e[j] for j in lIdxM]
    #             print "vrs_e!=0 : ", vrs_e
        vals_e_d = [k[0] for k in extraIncubent]
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


        # Forcing extraIncubent duration:  forall j, ej= dur(extraIncubent[j]), O otherwise "
        vars_e= vars_e_d +vars_e_0
        vals_e= vals_e_d+vals_e_0
        if(len(vars_e)>0):
            for o,ve in enumerate(vars_e):
                    c.linear_constraints.add(lin_expr = [cplex.SparsePair([vars_e[o]], [1])], senses = ["E"], rhs = [vals_e[o]])

        # Optional CUT   sum_j(e_j) <= obj(heu)
        if(len(e)>0):
            c.linear_constraints.add(lin_expr = [cplex.SparsePair(e, [1]*len(e))], senses = ["L"], rhs = [objIncubent])

        # adding the incubent as a start solution to cplex
        if len(all_vars)>0:
            c.MIP_starts.add(cplex.SparsePair(ind = all_vars, val = all_vals ), c.MIP_starts.effort_level.check_feasibility, "Heu")


    c.solve()

    return c.solution.get_status() ==101




if __name__ == '__main__':
    pass