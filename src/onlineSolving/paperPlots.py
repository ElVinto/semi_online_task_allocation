'''
Created on 26 Apr 2017

@author: varmant
'''


from serverPlots import *

def getPolicies():
    lHeu = [
        CONST_H_FMF,
        CONST_H_myFF,
        CONST_H_myBFD,
        CONST_H_mySS,
        CONST_H_myNF,
        CONST_H_myBFR,
        CONST_H_myHA,
        CONST_H_myMRD,
        CONST_H_myMRR
        ]
    return lHeu

def getPoliciesPlusCplex():
    lHeu = [
        CONST_H_FMF_CPLEX,
        CONST_H_myFF_CPLEX,
        CONST_H_myBFD_CPLEX,
        CONST_H_mySS_CPLEX,
        CONST_H_myNF_CPLEX,
        CONST_H_myBFR_CPLEX,
        CONST_H_myHA_CPLEX,
        CONST_H_myMRD_CPLEX,
        CONST_H_myMRR_CPLEX
        ]
    return lHeu


if __name__ == '__main__':

    # Experiments parameters
    lErr = [0, 50, 100,150, 200, 250, 300]
    lTw  = [0, 2, 10, 20, 30]
    lHeu = getPolicies()


    # Stats on benchmark

    tw = 2
#     csvFNameOut = writeCSV_tasksInTime(tw,123,124)
#     csvFNameOut = writeCSV_tasksInTime(tw)
#     plotNbTasksPerBucketInTime(csvFNameOut, tw)
#     plotBarDistNumTaskInBuck(csvFNameOut, tw)

#     plotCpuDistribution("../data/allTasks_U0.csv",hMax=7*24)
#     plotBarDurationDistribution("../data/allTasks_U0.csv",hMax=7*24)



#     # Result of the policies and the policies + cplex over one week
#
#     # ElapsedTime vs  RunTimeOfAllocatedMachines per Policy
#     tw,err=2,0
#
#     csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu=getPolicies(), tw=2, err=0, cum = True, xmin=None, xmax=None,cplex= False)
#     plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw),yLimit=(0,7000))
#
#     # ElapsedTime vs  RunTimeOfAllocatedMachines per Policy + Cplex NS
#     csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu=getPoliciesPlusCplex(), tw=2, err=0, cum = True, xmin=None, xmax=None,cplex= True)
#     plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw),yLimit=(0,7000))
#
#
#
#
#     # Result of the policies and the policies + cplex over the peak hour 123 124
#
#     # ElapsedTime vs  RunTimeOfAllocatedMachines per Policy tw=2 xmin=123, xmax=124
#     tw,err=2,0
#
#     csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu=getPolicies(), tw=2, err=0, cum = True, xmin=123, xmax=124,cplex= False, lbMachines = 180)
#
#     csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu=getPolicies(), tw=2, err=0, cum = False, xmin=123, xmax=124,cplex= False)
#     plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw),posPlot = "upper right",yLimit=(180,475))
#
#     # ElapsedTime vs  RunTimeOfAllocatedMachines per Policy + Cplex NS tw=2 xmin=123, xmax=124
#     csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu=getPoliciesPlusCplex(), tw=2, err=0, cum = True, xmin=123, xmax=124,cplex= True, lbMachines = 180)
#
#     csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu=getPoliciesPlusCplex(), tw=2, err=0, cum = False, xmin=123, xmax=124,cplex= True)
#     plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw),posPlot = "upper right",yLimit=(180,475))
#
#     # xmin, xmax = 123.0833, 124.083  tw =30 zoom <=>  xmin, xmax = 123,124 tw =2
#     tw,err=30,0
#
#     # ElapsedTime vs  RunTimeOfAllocatedMachines per Policy tw=30 xmin=123.0833, xmax=124.083
#     csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu=getPolicies(), tw=30, err=0, cum = True, xmin=123.083, xmax=124.083,cplex= False, lbMachines = 180)
#
#     # ElapsedTime vs  RunTimeOfAllocatedMachines per Policy + Cplex NS tw=30 xmin=123.0833, xmax=124.083
#     csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu=getPoliciesPlusCplex(), tw=30, err=0, cum = True, xmin=123.083, xmax=124.083,cplex= True, lbMachines = 180)
#
#
#
#
#
#
#     # result of the policies when varying the time windows
#
#     # TimeWindow Sizes vs  RunTimeOfAllocatedMachines per Heuristics
#
#     err = 0
#     csvFNameOut = writeCSV_tw_obj_heu(lTw, getPolicies(), err, xmin = None, xmax = None, cplex =False)
#     csvFNameOut = "Time-Step-Duration_Run-Time-Of-Allocated-Machines_Heuristic_err0.csv"
#     # copy BFD 0 at FMF 0 since FMF = FMF in online context
#     plotFromCSV(csvFNameOut,"(err:{0}%)".format(err), showMarkers =True , posPlot = 'at,upper right,1.0,1.0,3',yLimit=(4500,8100))

#     csvFNameOut = writeCSV_tw_obj_heu(lTw, getPoliciesPlusCplex() , err, xmin = None, xmax = None, cplex= True)
#     plotFromCSV(csvFNameOut,"(err:{0}%)".format(err), showMarkers =True, posPlot = 'at,upper right,1.0,1.0,3',yLimit=(4500,8100))
#
#     csvFNameOut = writeCSV_tw_obj_heu(lTw, getPolicies(), err, xmin = 123, xmax = 124, cplex =False)
#     plotFromCSV(csvFNameOut,"(err:{0}%)".format(err), showMarkers =True, posPlot = "upper right")
#
#     csvFNameOut = writeCSV_tw_obj_heu(lTw, getPoliciesPlusCplex() , err, xmin = 123, xmax = 124, cplex= True)
#     plotFromCSV(csvFNameOut,"(err:{0}%)".format(err), showMarkers =True, posPlot = "upper right")


#
#
#
#
#     # result of the policies when varying prediction error
#
#     # Error vs RunTimeOfAllocatedMachines per Heuristics
#
#     tw =2
#     csvFNameOut = writeCSV_error_obj_heu(lErr, getPolicies(), tw, cplex= False)
#     plotFromCSV(csvFNameOut,"(tw:{0}secs)".format(tw),showMarkers =True, posPlot = 'at,lower right,1.0,0.0,3',yLimit=(4500,8100))
#
#     csvFNameOut = writeCSV_error_obj_heu(lErr, getPoliciesPlusCplex(), tw, cplex= True)
#     plotFromCSV(csvFNameOut,"(tw:{0}secs)".format(tw),showMarkers =True, posPlot = "at,lower right,1.0,0.0,3",yLimit=(4500,8100))

#
#
#
#     # solving time of the policies in time
#
#     tw =2
#     err =0
# #
#     csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu(getPolicies(), tw, err, cum =False, cplex= False, nbTasksMin = 100,tLimit = tw)
#     plotBoxes(csvFNameOut)
#     writeCSV_Stat_SolvingTime_heu(getPolicies(), tw, err, cum =False, cplex= False, nbTasksMin = 100,tLimit = tw)
# ##     plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
#
#
#
#     csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu( getPoliciesPlusCplex(), tw,err,cum=False,nbTasksMin = 100,cplex= True,tLimit = tw)
#     plotBoxes(csvFNameOut)
#     writeCSV_Stat_SolvingTime_heu(getPoliciesPlusCplex(), tw, err, cum =False, cplex= True, nbTasksMin = 100,tLimit = tw)
##     plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))




# ------------------------------------------------------------------------------
# The starplot
# - Probably broken for now.
#-------------------------------------------------------------------------------
#     lErr = [0, 50, 100]
#     lTw  = [2] # [2, 10, 20, 30]
#     csvFNameOut = writeCSV_starPlot(lHeu, lErr, lTw)
    csvFNameOut = baseIn+"csv/radarT.csv"
    starPlotFromCSV(csvFNameOut,0.1)
