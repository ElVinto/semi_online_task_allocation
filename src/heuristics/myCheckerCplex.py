'''
Created on 22 Mar 2017

@author: varmant
'''

import time
import os

import threading
import logging

import sys
import cplex
from cplex._internal._constants import CPX_PARAM_EPGAP, CPX_PARAM_TILIM, CPX_STAT_OPTIMAL, CPXMIP_OPTIMAL, CPX_PARAM_ADVIND,CPX_PARAM_RINSHEUR
from cplex.callbacks import MIPInfoCallback

import operator
import subprocess
from const import *
from utils import *

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

class MyStoppingThreadWithArgs(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.kwargs = kwargs
        self.process = None
        return

    def run(self):
        print "Starting " + self.name
        logging.debug('running with %s and %s', self.args, self.kwargs)
        cmd = [ "bash", 'process.sh']
        self.process = p = subprocess.Popen(cmd,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline, b''):
            print ("-- " + line.rstrip())
        print "Exiting " + self.name
        return

    def stop(self):
        print "Trying to stop thread "
        if self.process is not None:
            self.process.terminate()
            self.process = None

# Example of thread
#
# thr = MyStoppingThreadWithArgs(...)
# thr.start()
# time.sleep(30)
# thr.stop()
# thr.join()
#
# def daemon():
#     logging.debug('Starting')
#     time.sleep(2)
#     logging.debug('Exiting')
#
# d = threading.Thread(name='daemon', target=daemon)
# d.setDaemon(True)
#
# def non_daemon():
#     logging.debug('Starting')
#     logging.debug('Exiting')
#
# t = threading.Thread(name='non-daemon', target=non_daemon)
#
# d.start()
# t.start()
#
# d.join(1)
# print 'd.isAlive()', d.isAlive()
# t.join()

class SearchInfoCallback(MIPInfoCallback):
    def __call__(self):
        with open(tmpFName,"wt") as f:
            print >> f, str(self.get_incumbent_objective_value())+","+str(self.get_best_objective_value())+","+str(100.0*self.get_MIP_relative_gap())



    def cplex(self, lMachines, lItems, cTime,  timelimit = None, incubent = None, extraIncubent=None, objIncubent =None,CODE_ASSERT_HEU_WITH_CPLEX=False):

        st = time.clock()

        if incubent is None:
            fName = self.dFiles[CONST_F_CPLEX]
        else:
            fName = self.dFiles[CONST_F_CPFMF]
        stBuck = cTime
        endBuck = stBuck + self.bucketSize


        if timelimit is not None:
            if timelimit<=0:
                for (i,j) in incubent:
                    self.assign(lMachines[j],lItems[i],cTime)
                with open(fName, "at") as pout:
                    print >> pout, "{0}, {1}, {2}, {3}, {4}, {5}".format(stBuck, endBuck,  objIncubent,  None, None, -1)
                return 0.0



        nItems = len(lItems)
        nBins = len(lMachines)


        c = cplex.Cplex()
        c.set_log_stream(None)
        c.set_error_stream(None)
        c.set_warning_stream(None)
        c.set_results_stream(None)
        #c.parameters.mip.strategy.probe.set(3)
        c.parameters._set(CPX_PARAM_EPGAP, .0)
        if timelimit == None:
            c.parameters.timelimit.set(self.bucketSize)
        else :
            c.parameters.timelimit.set(timelimit)

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

            # lMachines[j].lrt == maxRemEstDur

            if  len(lMachines[j].tasks)>0:
                maxRemEstDur = max([t.remEstDur for t in lMachines[j].tasks])
            else:
                maxRemEstDur =0.0


            lbs.append(int(maxRemEstDur))
            ubs.append(max(longestTask, int(maxRemEstDur)))
            e.append("e_" + str(j))
        caps = [m.capacities[CONST_LCPU] for m in lMachines]
#         c.variables.add(obj = caps, names = e, lb = lbs, ub = ubs, types = [c.variables.type.continuous] * nBins) # Faster but can be less Quality
        c.variables.add(obj = caps, names = e, lb = lbs, ub = ubs, types = [c.variables.type.integer] * nBins) # the max duration are int values

        #c.variables.add(names = e, lb = lbs, ub = ubs, types = ["I"] * nBins)

        # For all items : Assignment constraint
        for i in range(nItems):
            vrs = [x[i][j] for j in range(nBins)]
            cts = [1] * nBins
            c.linear_constraints.add(lin_expr = [cplex.SparsePair(vrs, cts)], senses = ["E"], rhs = [1])

        ## Load constraint for each machine
        # The sum of the reqs for any task assigned to it must be lower than the machine capacity
        for j in range(nBins):
            vrs = [x[i][j] for i in range(nItems)]
            cts = [lItems[i].reqs[CONST_LCPU] for i in range(nItems)]
            remCap = lMachines[j].capacities[CONST_LCPU] - lMachines[j].usages[CONST_LCPU]

            c.linear_constraints.add(lin_expr = [cplex.SparsePair(vrs, cts)], senses = ["L"], rhs = [remCap])
#             c.linear_constraints.add(lin_expr = [cplex.SparsePair(vrs, cts)], senses = ["G"], rhs = [0]) # Optimisation


#         for i in range(nItems):
#             for j in range(nBins):
#                 # 0 <= x_ij * remEstDur_i
#                 c.linear_constraints.add(lin_expr = [cplex.SparsePair([x[i][j]], [1])], senses = ["G"], rhs = [0])
#
#                 # x_ij * remEstDur_i <= e_j
#                 redj = [t.remEstDur for t in lItems]
#                 c.linear_constraints.add(lin_expr = [cplex.SparsePair([x[i][j]], redj)], senses = ["L"], rhs = [e[j]])

        # Write constraint on e_j
        for j in range(nBins):
            # TODO : 0 <= e_j - x_ij * remEstDur_i
            for i in range(nItems):
                vrs = [e[j],x[i][j]]
                cts = [1,-lItems[i].remEstDur ]
                c.linear_constraints.add(lin_expr = [cplex.SparsePair(vrs, cts)], senses = ["G"], rhs = [0])
#                 colName
#                 c.linear_constraints.add(lin_expr = [[[x[i][j], e[j]],[lItems[i].remEstDur, 1]]], senses = ["L"], rhs =M[j])

            #lhs = []
            #rhs = []
            #c.linear_constraints.add(lin_expr = [cplex.SparsePair([x[i][j]], [1])], senses = ["G"], rhs = [0])

            # e_j - x_ij * remEstDur_i <= Mj
#             vrs = [x[i][j] for i in range(nItems)]
#             cts = [0 for _ in range(nItems)]
            #c.linear_constraints.add(lin_expr = [cplex.SparsePair([x[i][j] for i in range(nItems)], cts) ], senses = ["L"], rhs = [M[j]] * nItems)



        if  incubent is not None:
            # We set incumbent just before the call to solve
            c.parameters._set(CPX_PARAM_ADVIND, 2)
            c.parameters._set(CPX_PARAM_RINSHEUR, 500)
            # The incumbent is a set of sparse pairs


#             print "incubent {0} ".format(incubent)
#             print "nBins {0} nItems {1}".format(nBins,nItems)
#             print "x: {0}".format(x)

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

            if CODE_ASSERT_HEU_WITH_CPLEX:
#                 print "Forcing Incubent assignement:  forall xij, xij= e_(incubent[j]) "
                for (i,j) in incubent:
#                     print " {0} == {1}".format(x[i][j],1)
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


            if CODE_ASSERT_HEU_WITH_CPLEX:
#                 print "Forcing extraIncubent duration:  forall j, ej= dur(extraIncubent[j]), O otherwise "
                vars_e= vars_e_d +vars_e_0
                vals_e= vals_e_d+vals_e_0
                if(len(vars_e)>0):
                    for o,ve in enumerate(vars_e):
#                         print " {0} == {1}".format(vars_e[o],vals_e[o])
                        c.linear_constraints.add(lin_expr = [cplex.SparsePair([vars_e[o]], [1])], senses = ["E"], rhs = [vals_e[o]])

            # Optional CUT   sum_j(e_j) <= obj(heu)
            if(len(e)>0):
                c.linear_constraints.add(lin_expr = [cplex.SparsePair(e, [1]*len(e))], senses = ["L"], rhs = [objIncubent])

            if len(all_vars)>0:
                c.MIP_starts.add(cplex.SparsePair(ind = all_vars, val = all_vals ), c.MIP_starts.effort_level.check_feasibility, "Heu")


#         c.write("debug.lp")

        global tmpFName
        tmpFName=self.dFiles[CONST_F_TMP]
        with open(tmpFName,"wt") as f:
            print >> f, ""

        c.register_callback(SearchInfoCallback)
        c.solve()



        cplexTime = time.clock() -st



        if cplexTime> self.bucketSize +1.0:
            print " Cplex was to long to Finish using incubent Solution from Heu"
            if objIncubent is not None:
                for (i,j) in incubent:
                    self.assign(lMachines[j],lItems[i],cTime)
                    with open(fName, "at") as pout:
                        print >> pout, "{0}, {1}, {2}, {3}, {4}, {5}".format(stBuck, endBuck,  objIncubent,  None, None, -1)
                    return 0.0
            else:
                if CODE_ASSERT_HEU_WITH_CPLEX:
                    assert(False)
                print "Calling ff"
                return self.firstFit(lMachines, lItems, cTime)

        sol = c.solution
#         print "solution Status: "+str(c.solution.get_status())


        isCplexSol =False

        if objIncubent is None:
            if CODE_ASSERT_HEU_WITH_CPLEX:
                assert(False)
            try:
                # First the program checks that a solution can be extracted
                for i in range(len(lItems)):
                    xi = sol.get_values(x[i])
                    m = [lMachines[j] for j, xij in enumerate(xi) if int(xij) == 1][0]

                for i in range(len(lItems)):
                    xi = sol.get_values(x[i])
                    m = [lMachines[j] for j, xij in enumerate(xi) if int(xij) == 1][0]
                    self.assign(m, lItems[i], cTime)
                isCplexSol =True
            except Exception:
                isCplexSol =False
                print "Calling ff"
                return self.firstFit(lMachines, lItems, cTime)

        else:
            if c.solution.get_status() ==108:
                isCplexSol =False
                print "Infeasible  Sol from incubent"
                if CODE_ASSERT_HEU_WITH_CPLEX:
                    assert(False)

                for (i,j) in incubent:
                    self.assign(lMachines[j],lItems[i],cTime)
            else:
                try:
                    cplexObj = c.solution.get_objective_value()

                    if cplexObj <= objIncubent:
                        try:
                            # First the program checks that a solution can be extracted
                            for i in range(len(lItems)):
                                xi = sol.get_values(x[i])
                                m = [lMachines[j] for j, xij in enumerate(xi) if int(xij) == 1][0]

                            for i in range(len(lItems)):
                                xi = sol.get_values(x[i])
                                m = [lMachines[j] for j, xij in enumerate(xi) if int(xij) == 1][0]
                                self.assign(m, lItems[i], cTime)
                            isCplexSol =True
                        except Exception:
                            isCplexSol =False
        #                     print "Sol from incubent"
                            for (i,j) in incubent:
                                self.assign(lMachines[j],lItems[i],cTime)
                    else:

                        print "UnExpected objCplex:{0} > objHeu:{1}, nbItems {2}, using incubent from Heu".format(cplexObj,objIncubent,len(lItems))
                        if CODE_ASSERT_HEU_WITH_CPLEX:
                            assert(False)
                        isCplexSol =False
        #                 print "Sol from incubent"
                        for (i,j) in incubent:
                            self.assign(lMachines[j],lItems[i],cTime)

                except Exception as expt:
                    print "Unknown Issue  Sol from Incubent"
                    if CODE_ASSERT_HEU_WITH_CPLEX:
                        assert(False)
                    isCplexSol =False
                    for (i,j) in incubent:
                        self.assign(lMachines[j],lItems[i],cTime)


        if c.solution.get_status() == CPXMIP_OPTIMAL or c.solution.get_status()==CPX_STAT_OPTIMAL:
            with open(fName, "at") as pout:
                print >> pout, "{0}, {1}, {2}, {3}, {4}, {5}".format(stBuck, endBuck,  c.solution.get_objective_value(),  c.solution.get_objective_value(), 0.0,  c.solution.get_status())
            return c.solution.get_objective_value()
        else:
            with open(tmpFName,"rt") as f:
                for l in f:
                    if l.strip() == "":
                        if isCplexSol:
                            with open(fName, "at") as pout:
                                print >> pout, "{0}, {1}, {2}, {3}, {4}, {5}".format(stBuck, endBuck,  c.solution.get_objective_value(),  None, None, c.solution.get_status())
                            return c.solution.get_objective_value()
                        else:
                            with open(fName, "at") as pout:
                                print >> pout, "{0}, {1}, {2}, {3}, {4}, {5}".format(stBuck, endBuck,  objIncubent,  None, None, -1)

                    else:
                        if isCplexSol:
                            vals = l.strip().split(",")
                            with open(fName, "at") as pout:
                                print >> pout, "{0}, {1}, {2}, {3}, {4}, {5}".format(stBuck, endBuck,  vals[0],  vals[1], vals[2],  c.solution.get_status())
                            return c.solution.get_objective_value()
                        else:
                            with open(fName, "at") as pout:
                                print >> pout, "{0}, {1}, {2}, {3}, {4}, {5}".format(stBuck, endBuck,  objIncubent,  None, None, -1)



        return True


