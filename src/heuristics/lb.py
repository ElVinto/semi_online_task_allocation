import math
from utils import *
from os import path
import os
import time
import const

def lb_inBucket(tasks, bucketSize, cap, cTime, verb):

    # The set of tasks that will not finish in the bucket.
    lb = 0
    t1 = []
    t2 = []
    for t in tasks:
        # tasks already assigned
        if t.stTime != None:
            # RECALL self.cTime is the started time of the bucket
            # RECALL t.remDur has not been updated yet
            # tasks  finishing after the bucket
            if t.stTime + t.dur * CONST_SECINMILISEC - cTime > bucketSize * CONST_SECINMILISEC:
#                 print "\tfinishing outside bucket  {0}".format(t)
                t1.append(t)
                lb += t.reqs["cpu"] * bucketSize

            # tasks finishing in bucket.
            else:
                # tasks finishing between ]cTime,cTime+bucketSize]
                if t.stTime + t.dur * CONST_SECINMILISEC - cTime > 0:
#                     print "\tfinishing in bucket  {0}".format(t)
                    t2.append(t)
                    lb += (t.reqs["cpu"] * (t.stTime + t.dur * CONST_SECINMILISEC - cTime))/float(CONST_SECINMILISEC)





    # The lower bound should be sum(bucketSize * lb1(t1))
    # + the rest
    if verb: print "\t{0} seconds is the LB allocated in current bucket ".format(lb)
    return lb

def lb2_inBucket(tasks, bucketSize, cap, cTime, verb):

    # The set of tasks that will not finish in the bucket.
    
    aliveTasks = [t for t in tasks if t.stTime != None]
            
    sorted_tasks = sorted(aliveTasks, key = lambda t : bucketSize if t.stTime + t.dur * CONST_SECINMILISEC - cTime > bucketSize * CONST_SECINMILISEC else (t.stTime + t.dur * CONST_SECINMILISEC - cTime)/float(CONST_SECINMILISEC), reverse = True)
    
    defaultMachineCPUCapacity =1
    
    lb2 = 0 # The default cpu capacity to one machine is one
    if sorted_tasks[0].stTime + sorted_tasks[0].dur * CONST_SECINMILISEC - cTime > bucketSize * CONST_SECINMILISEC:
        lb2+= bucketSize*defaultMachineCPUCapacity
    else:
        lb2+= ((sorted_tasks[0].stTime + sorted_tasks[0].dur * CONST_SECINMILISEC - cTime)/float(CONST_SECINMILISEC))*defaultMachineCPUCapacity
        
    resourceAllocToCurrentMachine = sorted_tasks[0].reqs["cpu"]
    for i in range(1, len(sorted_tasks)):
        t = sorted_tasks[i]
        resourceAllocToCurrentMachine += t.reqs["cpu"]
        if resourceAllocToCurrentMachine>=defaultMachineCPUCapacity:
            if t.stTime + t.dur * CONST_SECINMILISEC - cTime > bucketSize * CONST_SECINMILISEC:
                lb2+= bucketSize*defaultMachineCPUCapacity
            else:
                lb2+= ((t.stTime + t.dur * CONST_SECINMILISEC - cTime)/float(CONST_SECINMILISEC))*defaultMachineCPUCapacity
            
            resourceAllocToCurrentMachine= resourceAllocToCurrentMachine-defaultMachineCPUCapacity;
            
    if verb: print "\t{0} seconds is the LB2 allocated in current bucket ".format(lb2)
    return lb2


#    # DEAD CODE MORE PRECISE LOWER BOUND TO CHECK
#
#     #lb = int(math.ceil(sum(i.reqs["cpu"] for i in t1) / float(cap))) * bucketSize
#
#     sorted_tasks = sorted(t2, key = lambda t : t.remDur if t.stTime != None else t.dur, reverse = True)
#
#     lb1 = int(math.ceil(sum(i.reqs["cpu"] for i in sorted_tasks) / float(cap)))
#
#
#     #assert(lb1 != 0), "Can not have need 0 machine"
#     cumulReq = [0]
#     for i in sorted_tasks:
#         cumulReq.append(cumulReq[-1] + i.reqs["cpu"])
#     cumulReq = cumulReq[1:]
#
#     lm = []
#
#     for m in range(lb1):
#         tasksInRange = [j for idx, j in enumerate(sorted_tasks) if
#                         cumulReq[idx] > (m) * cap
#                         and
#                         cumulReq[idx] <= (m + 1) * cap
#                         ]
#
#         #print len(tasksInRange)
#         tir = [t.remDur if t.stTime != None else t.dur for t in tasksInRange]
#         #tir.append(0.0)
#         lm.append(min(max(tir), bucketSize))
#     print "\tLB in bucket {0}".format(lb + sum(i * cap for i in lm))
#     return lb + sum(i * cap for i in lm)


#def lb_4(tasks, machines, cap):

    ## Sorting the tasks
    #sorted_tasks = sorted(tasks, key = lambda t : t.remdur, reverse = True)
    #lb1 = int(math.ceil(sum(i.reqs["cpu"] for i in tasks) / float(cap)))

    #cumulReq = [0]
    #for i in sorted_tasks:
        #cumulReq.append(cumulReq[-1] + i.reqs["cpu"])
    #cumulReq = cumulReq[1:]

    #lm = []
    #for m in range(lb1):
        #tasksInRange = [j for idx, j in enumerate(sorted_tasks) if
                        #cumulReq[idx] > (m) * cap
                        #and
                        #cumulReq[idx] <= (m + 1) * cap
                        #]


        #tir = [j.remdur for j in tasksInRange]
        ##print len(tir)
        #if len(tir) != 0:
            #lm.append(max(tir))

    #cpt = 0
    #for i in lm:
        #cpt += i * cap
    #return cpt

# if __name__ == '__main__':

    #fName = "../data/googleSeq/inst_10_2.csv"
    #lItems = parseInstance(fName, floats = True)
    #lMachines = [Machine(i + 1, 0.5, 0.5) for i in range(len(lItems))]

    #lb = lb_4(lItems, lMachines, 0.5)
    #print "LB ", lb

    #assert(False)

#     for b in ["googleRand", "googleSeq", "integerInstances"]:
#         for inst in os.listdir("../data/{0}/".format(b)):
#             if inst.endswith(".csv"):
#                 iNum = inst.split("_")[2].split(".")[0]
#                 print "../data/{0}/{1}".format(b, inst)
#                 if b == "integerInstances":
#                     lItems = parseInstance("../data/{0}/{1}".format(b, inst), floats = False)
#                     lMachines = [Machine(i + 1, 100, 100) for i in range(len(lItems))]
#                     cap = 100
#                 else:
#                     lItems = parseInstance("../data/{0}/{1}".format(b, inst), floats = True)
#                     lMachines = [Machine(i + 1, 0.5, 0.5) for i in range(len(lItems))]
#                     cap = 0.5
#                 st = time.clock()
#                 lb = lb_4(lItems, lMachines, cap)
#                 outFile = "../../results/{0}/lbs/lbs.csv".format(b)
#                 with open(outFile, "at") as of:
#                     print >> of, "{0}, {1}, {2}, {3}".format(len(lItems), iNum, lb, time.clock() - st)
                #print "{0}, {1}, {2}, {3}".format(len(lItems), iNum, lb, time.clock() - st)


