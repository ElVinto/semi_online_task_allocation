import sys
import os
import random
from collections import OrderedDict
from numpy import mean, median
from matplotlib.pyplot import axis
sys.path.append('../heuristics/')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from itertools import product
from itertools import izip

from const import *


from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from spider import *


def plotBarDurationDistribution(dataFile, hMin = None, hMax = None):
    plotFName = "{0}distDuration.pdf".format(baseOutPlot)
    print plotFName
    pp = PdfPages(plotFName)


    lDuration =[]
    with open(dataFile, "rt") as f:
        for line in f:
            vals = line.strip().split(", ")

            timeStamp = float(vals[0])/(1000000.0*3600.0)
            if hMin != None:
                if timeStamp < hMin:
                    continue
            if hMax != None:
                if timeStamp > hMax:
                    break

            dur = int(vals[4])
            if dur >0:
                lDuration.append(dur)


    nbTasks = []
    nbTasks.append(sum(1 for d in lDuration if d <= 60 ))
    nbTasks.append(sum(1 for d in lDuration if d > 60 and d<=600))
    nbTasks.append(sum(1 for d in lDuration if d >600 and d<=3600 ))
    nbTasks.append(sum(1 for d in lDuration if d >3600 and d<=3600*10 ))
    nbTasks.append(sum(1 for d in lDuration if d >3600*10 and d<=3600*24 ))
    nbTasks.append(sum(1 for d in lDuration if d >3600*24 ))

    ind = np.arange(len(nbTasks))  # the x locations for the groups
    width = 1.0       # the width of the bars




    fig, ax = plt.subplots()
    rects1 = ax.bar(ind, nbTasks, width, color='blue')

    plt.yscale('log', nonposy='clip')


    ax.set_ylabel('Incoming tasks',fontsize='18')
#     ax.set_title("Distribution of task durations")
    ax.set_xticks(ind + width)
    ax.set_xticklabels(('1 min', '10 mins','1 hour','10 hours','1 day','>1 day'))
    ax.set_xlabel('time duration',fontsize='18')
    plt.tight_layout()




    pp.savefig(fig,dpi=600)
    pp.close()

def plotCpuDistribution(dataFile, hMin = None, hMax = None):

    plotFName = "{0}distCPU.pdf".format(baseOutPlot)
    print plotFName
    pp = PdfPages(plotFName)
    fig, ax1 = plt.subplots()

    lCpu =[]
    with open(dataFile, "rt") as f:
        for line in f:
            vals = line.strip().split(", ")

            timeStamp = float(vals[0])/(1000000.0*3600.0)
            if hMin != None:
                if timeStamp < hMin:
                    continue
            if hMax != None:
                if timeStamp > hMax:
                    break

            cpu = float(vals[2])
            lCpu.append(cpu)


    plt.hist(lCpu, bins = 10)
    plt.yscale('log', nonposy='clip')


#     plt.title("Distribution of task cpu requirements")
    plt.xlabel("Cpu requirements in percent",fontsize='18')
    plt.ylabel("Incoming tasks",fontsize='18')

    plt.tight_layout()
    pp.savefig(fig)
    pp.close()


def plotBarDistNumTaskInBuck(fIn, tw):
        # baseOutPlot
    plotFName = "{0}distTasksPerBucket_tw{1}.pdf".format(baseOutPlot, tw)
    print plotFName
    pp = PdfPages(plotFName)
    fig, ax = plt.subplots()

    nbTasks = []
    with open(fIn, "rt") as f:
        for i, line in enumerate(f):
            if i == 0:
                headers = line.strip().split(", ")
            else:
                line = map(int, line.strip().split(", "))
                #time.append(line[0])
                nbTasks.append(int(line[2]))
                #cumTasks.append(line[3])
                #tInSys.append(line[4])




    nbOccTasksPerTW = []
    nbOccTasksPerTW.append(sum(1 for nb in nbTasks if nb <= 10 ))
    nbOccTasksPerTW.append(sum(1 for nb in nbTasks if nb > 10 and nb<=20))
    nbOccTasksPerTW.append(sum(1 for nb in nbTasks if nb >20 and nb<=50 ))
    nbOccTasksPerTW.append(sum(1 for nb in nbTasks if nb >50 and nb<=100 ))
    nbOccTasksPerTW.append(sum(1 for nb in nbTasks if nb >100 and nb<=200 ))
    nbOccTasksPerTW.append(sum(1 for nb in nbTasks if nb >200 and nb<=500 ))
    nbOccTasksPerTW.append(sum(1 for nb in nbTasks if nb >500 and nb<=1000 ))
    nbOccTasksPerTW.append(sum(1 for nb in nbTasks if nb >1000 ))

    ind = np.arange(len(nbOccTasksPerTW))  # the x locations for the groups
    width = 1.0       # the width of the bars




    fig, ax = plt.subplots()
    ax.bar(ind, nbOccTasksPerTW, width, color='blue')

    plt.yscale('log', nonposy='clip')



#     ax.set_title("Distribution of the number of tasks per bucket of {0} seconds".format(tw))
    ax.set_xticks(ind + width)
    ax.set_xticklabels(('10', '20','50','100','200','500','1000','>1000'))
    ax.set_xlabel("Incoming tasks",fontsize='18')
    ax.set_ylabel("Time-steps of {0} secs".format(tw),fontsize='18')


    plt.tight_layout()
    pp.savefig(fig)
    pp.close()


def plotDistNumTaskInBuck(fIn, tw):
        # baseOutPlot
    plotFName = "{0}disttasksPerBucket_tw{1}.pdf".format(baseOutPlot, tw)
    print plotFName
    pp = PdfPages(plotFName)
    fig, ax1 = plt.subplots()

    #time = []
    nTasskPerTW = []
    #cumTasks = [0]
    #tInSys = []
    with open(fIn, "rt") as f:
        for i, line in enumerate(f):
            if i == 0:
                headers = line.strip().split(", ")
            else:
                line = map(int, line.strip().split(", "))
                #time.append(line[0])
                nbTasks = int(line[2])
                nTasskPerTW.append(nbTasks)
                #cumTasks.append(line[3])
                #tInSys.append(line[4])


    plt.hist(nTasskPerTW, bins = 200)

    plt.yscale('log', nonposy='clip')
    plt.ylim(0.8,max(nTasskPerTW))

    plt.title("Distribution of the number of tasks per bucket of {0} seconds".format(tw))
    plt.xlabel("Number of Tasks per time-step of {0} seconds".format(tw))
    plt.ylabel("Frequency")

    plt.tight_layout()
    pp.savefig(fig)
    pp.close()


def plotNbTasksPerBucketInTime(fIn, tw):

    # baseOutPlot
    plotFName = "{0}distTasksPerBucketInTime_tw{1}.pdf".format(baseOutPlot, tw)
    print plotFName
    pp = PdfPages(plotFName)

    time = []
    nTasskPerTW = []
    cumTasks = [0]
    tInSys = []
    with open(fIn, "rt") as f:
        for i, line in enumerate(f):
            if i == 0:
                headers = line.strip().split(", ")
            else:
                line = map(int, line.strip().split(", "))
                time.append(line[0])

                nTasskPerTW.append(line[2])
                cumTasks.append(line[3])
                tInSys.append(line[4])


    #fig = plt.figure()
    fig, ax1 = plt.subplots()
#     plt.title("Number of tasks in buckets of {0} seconds over time.".format(tw))

    fts = min(time)
    lts = max(time)


    span = lts - fts
    #labs = [i / 3600 / 24  for i in xrange(span) if i % (3600 * 24) == 0]
    #pos = [i for i in xrange(span) if i % (3600 * 24) == 0]
    labs = [i / 3600 for i in xrange(span) if i % (3600 * 20) == 0]
    pos = [i for i in xrange(span) if i % (3600 * 20) == 0]


    plt.xticks(pos, labs)

#     plt.yscale('log', nonposy='clip')

    legend = plt.legend(loc='upper left', shadow = False)

    plt.xlabel("Elapsed time in hours",fontsize='18')
    plt.ylabel("Incoming tasks per time-step of {0} secs".format(tw),fontsize='18')


    plt.plot(time, nTasskPerTW)
    #plt.plot(time, tInSys, 'o')

    ax2 = ax1.twinx()
    plt.ylabel("Cumulative number of incoming tasks",fontsize='18')
#     plt.yscale('log', nonposy='clip')
    plt.plot(time, cumTasks[1:], linestyle='--', color='r', linewidth=3)


    plt.tight_layout()
    pp.savefig(fig)
    pp.close()

def plotFromCSV(csvFName,otherParamsInTitle=None, showMarkers =False, posPlot = "upper left", yLimit =None):
    x_y_s_opt = csvFName.split(".")[0]
    plotFName = baseOutPlot+(x_y_s_opt)+'.pdf'
    print plotFName
    pp = PdfPages(plotFName)

    # Fetch the data
    xLabel = None
    xUnit = None
    yLabel = None
    yUnit = None

    i2col = {}

    colName2yVals = {}
    colName2xVals = {}

    with  open(baseInCsvToPlot+csvFName,"rt") as f:
        for l in f:
            if xLabel==None:
                vals =  l.strip().split(",")
                for i in range(len(vals)):
                    if i==0:
                        xLabel = vals[i].split("_")[0]
                        xUnit =  vals[i].split("_")[1]
                    else:
                        yUnit = vals[i].split("_")[-1]
                        serieName =vals[i].replace("_"+yUnit,"")
                        i2col[i]=serieName
                        colName2yVals[serieName]=[]
                        colName2xVals[serieName]=[]

            else:
                vals =  l.strip().split(",")
                for i in range(len(vals)):
                    if i!=0 :
                        if vals[i] != "None":
                            colName2yVals[i2col[i]].append(float(vals[i]))
                            colName2xVals[i2col[i]].append(float(vals[0]))

#     fig = plt.figure()
    fig, ax = plt.subplots()

    plt.rcParams.update({'font.size': 15})
    valXYS= x_y_s_opt.split("_")


#     if otherParamsInTitle is not None:
#         plt.title(" {0} vs {1} per {2} \n {3}".format(valXYS[1],valXYS[0],valXYS[2],otherParamsInTitle))
#     else:
#         plt.title(" {0} vs {1} per {2} \n {3}".format(valXYS[1],valXYS[0],valXYS[2]))




    for k, v in colName2yVals.iteritems():
        if k != xLabel:
#             plt.plot(colName2xVals[k], v, label=k.replace("my",""))
            if showMarkers :
                plt.plot(colName2xVals[k], v, label=relabel[k], color = recolor[k], marker ='o',linewidth=2)
            else:
                plt.plot(colName2xVals[k], v, label=relabel[k], color = recolor[k],linewidth=2)



    # Now add the legend with some customizations.
#     plt.legend(loc='upper left', shadow=False)

    plt.grid(True)

#
    if "at" in posPlot :
        aPosLegend = posPlot.split(',')
        l = aPosLegend[1]
        anchor = (float(aPosLegend[2]),float(aPosLegend[3]))
        nc = int(aPosLegend[4])

        leg =ax.legend(loc=l, bbox_to_anchor=anchor, fontsize = '16',
          ncol=nc, fancybox=False, shadow=False)
    else:
        leg =ax.legend(loc=posPlot,  fancybox=False, shadow=False,fontsize = '16')
    # transparency
    frame = leg.get_frame()
    frame.set_alpha(0.5)
#     frame.set_linewidth(0)


    if yLimit is not None :
        plt.ylim(yLimit)



    plt.xlabel("{0} in {1}".format(valXYS[0].lower().replace('-',' '),xUnit),fontsize='18')
    if yUnit !='unit':
        plt.ylabel("{0} in {1}".format(valXYS[1].lower().replace('-',' '),yUnit),fontsize='18')
    else:
        plt.ylabel("{0}".format(valXYS[1].lower().replace('-',' ')),fontsize='18')


    pp.savefig(fig, dpi=1200, bbox_inches='tight')
    pp.close()

def reWriteLabel(labelName):
    nvLabel=''
    for l in labelName:
        if l.isupper():
            nvLabel+=' '+l
        else:
            nvLabel+=l
    return nvLabel

def plotBoxes(csvFName):
    x_y_s_opt = csvFName.split(".")[0]
    plotFName = baseOutPlot+(x_y_s_opt)+'.pdf'
    print plotFName
    pp = PdfPages(plotFName)


    # Fetch the data
    xLabel = None
    xUnit = None
    yLabel = None
    yUnit = None

    i2col = {}

    colName2yVals = {}
    colName2xVals = {}


    with  open(baseInCsvToPlot+csvFName,"rt") as f:
        for l in f:
            if xLabel==None:
                vals =  l.strip().split(",")
                for i in range(len(vals)):
                    if i==0:
                        xLabel = vals[i].split("_")[0]
                        xUnit =  vals[i].split("_")[1]
                    else:
                        yUnit = vals[i].split("_")[-1]
                        serieName =vals[i].replace("_"+yUnit,"")
                        i2col[i]=serieName
                        colName2yVals[serieName]=[]
                        colName2xVals[serieName]=[]

            else:
                vals =  l.strip().split(",")
                for i in range(len(vals)):
                    if i!=0 :
                        if vals[i] != "None":
                            colName2yVals[i2col[i]].append(float(vals[i]))
                            colName2xVals[i2col[i]].append(float(vals[0]))

    fig, ax = plt.subplots()
    data = []
    labs = []

    for k, v in colName2yVals.iteritems():
        labs.append(relabel[k].replace('_NS',''))
        data.append(v)
#         data.append([t for t in v if t>=0.01 ])

    bp = plt.boxplot(data)



    plt.ylabel('solving time in seconds',fontsize='18')

    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='blue', marker='+')


    locations = range(1, len(labs) + 1) # rotate the labels
    plt.xticks(locations, labs,fontsize='16')
#     if 'Cplex' in csvFName:
#         plt.xlabel('Policies + Neighborhood Searh (NS)',fontsize='18')
#     else:
#         plt.xlabel('Policies ',fontsize='18')
    plt.subplots_adjust(bottom=0.07, left=0.10 )

    # Now add the legend with some customizations.
#     legend = plt.legend(loc='upper left')


    pp.savefig(fig, dpi=1200, bbox_inches='tight')

    pp.close()




def writeCSV_tasksInTime(tw,hMin=None, hMax=None):

    interval =''
    if hMin is not None and hMax is not None:
        interval +='_peak'
        if hMin is not None:
            interval +='_'+str(hMin)
        if hMax is not None :
            interval +='_'+str(hMax)

    fOut = "{0}csv/numTasksInTime_tw{1}{2}.csv".format(baseIn, tw,interval)
    fIn  = "{0}lb_allTasks_U0_myFF_DDUR_{1}.csv".format(baseIn, tw)
    print fOut
    print fIn

    with open(fIn, "rt") as f:
        with open(fOut, "wt") as g:
            print >> g, "ct, nct, nBuckTasks, cnBuckTasks, nSimTasks, cnSimTasks"

        nBuckTasks = cnBuckTasks = nSimTasks = cnSimTasks = 0

        for l in f:
            line = map(int, map(float, l.strip().split(", ")))

            cTime  = line[0] # in seconds
            if hMin is not None:
                if cTime<hMin*3600:
                    continue
            if hMax is not None:
                if cTime > hMax*3600:
                    break


            ncTime = line[1]
            nBuckTasks = line[3]

            # TODO : FIX the missing nSimTasks
            #print line
            #nSimTasks = line[4]
            nSimTasks = 0

            cnBuckTasks += nBuckTasks
            cnSimTasks  += nSimTasks

            with open(fOut, "at") as g:
                print >> g, "{0}, {1}, {2}, {3}, {4}, {5}".format(cTime, ncTime, nBuckTasks, cnBuckTasks, nSimTasks, cnSimTasks)

    return fOut

def writeCSV_ElapseTime_Obj_tw(lTw, h, err, cum = False, xmin = None, xmax = None, cplex =False):

    xLabel = "ElapsedTime"
    xUnit = "hours"

    if cum:
        yLabel = "CumulativeRunTimeOfAllocatedMachines"
        yUnit = "hours"
    else:
        yLabel = "RunTimeOfAllocatedMachines"
        yUnit = "minutes"

    seriesName = "TimeWindow"
    if cplex:
        seriesName += "Cplex"

    if xmin is not None and xmax is not None:
        seriesName +='_peak'
        if xmin is not None:
            seriesName +='_'+str(xmin)
        if xmax is not None :
            seriesName +='_'+str(xmax)

    csvFNameOut = "{0}_{1}_{2}_h{3}_err{4}.csv".format(xLabel,yLabel,seriesName, h, err)
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "usage_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict([]) # x coord, s serie name, y coord

    for tw in lTw:
        # FMF has no 0* time window lenght
        if h in CONST_NOPLOT_TW0 and tw == 0: continue

        if tw == 0:
            fName = baseName + str(err) + "_" + h + "_" + "LIST" + "_" + "2" + ".csv"
        else:
            fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"
        print fName
        with open(fName, "rt") as f:
            totScore = 0
            for line in f:
                x = float(line.strip().split(", ")[0])/(1000000.0*3600)
                y = float(line.strip().split(", ")[-1])
                if xmin is not None :
                    if x < xmin: continue
                if xmax is not None :
                    if x > xmax: break
                if cum:
                    y +=  totScore
                    totScore = y
                    y = y / 3600.0
                else:
                    y = y / 60.0

                if not x in x_s_y:
                    x_s_y.update({x : {tw : y}})
                else:
                    x_s_y[x].update({tw : y})

    #enriching x_s_y to map each x to a serieName and a value or None
    #TODO : Get rid of the FMF label.
    for x in  x_s_y.keys():
        for tw in lTw:
            if h in CONST_NOPLOT_TW0 and tw == 0: continue
            if  tw not in x_s_y[x].keys():
                #print x_s_y[x]
                x_s_y[x].update({tw : "None"})


    OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))

    hLine = "{0}_{1}".format(xLabel, xUnit)
    b = True
    with open(fNameOut, "wt") as g:

        numLine=0
        for x, s_y in x_s_y.iteritems():

            numLine += 1

            line = str(x)

            for s, y in s_y.iteritems():
                line += "," + str(y)

                if b:
                    hLine += "," + str(s)  + "_" + yUnit
            if b:
                print >> g, "{0}".format(hLine)
                b = False

            print >> g, "{0}".format(line)

    return csvFNameOut



def writeCSV_ElapseTime_Obj_err(lErr, h, tw, cum = False, xmin = None, xmax = None, cplex =False):
    xLabel = "ElapsedTime"
    xUnit = "hours"
    if h in CONST_NOPLOT_TW0 and tw == 0: return None
    #Warning(tw == 0 and h in CONST_NOPLOT_TW0), "Can not plot tw=0 for {0}".format(h)

    if cum:
        yLabel = "CumulativeRunTimeOfAllocatedMachines"
        yUnit = "hours"
    else:
        yLabel = "RunTimeOfAllocatedMachines"
        yUnit = "minutes"

    seriesName = "PredictionError"
    if cplex:
        seriesName += "Cplex"

    if xmin is not None and xmax is not None:
        seriesName +='_peak'
        if xmin is not None:
            seriesName +='_'+str(xmin)
        if xmax is not None :
            seriesName +='_'+str(xmax)

    csvFNameOut = "{0}_{1}_{2}_h{3}_tw{4}.csv".format(xLabel,yLabel,seriesName, h,tw)
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "usage_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict([]) # x coord, s serie name, y coord


    for err in lErr:

        if tw == 0:
            fName = baseName + str(err) + "_" + h + "_" + "LIST" + "_" + str(2) + ".csv"
        else:
            fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"
        print fName
        with open(fName, "rt") as f:
            totScore = 0
            for line in f:
                x = float(line.strip().split(", ")[0])/(1000000.0*3600)
                y = float(line.strip().split(", ")[-1])
                if cum:
                    y +=  totScore
                    totScore =y
                    y=y/3600.0
                else:
                    y=y/60.0

                if not x in x_s_y:
                    x_s_y.update({x : {err : y}})
                else:
                    x_s_y[x].update({err : y})

    #enriching x_s_y to map each x to a serieName and a value or None
    for x in  x_s_y.keys():
        for e in lErr:
            if  e not in x_s_y[x].keys():
                x_s_y[x].update({err : "None"})


    OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))

    hLine = "{0}_{1}".format(xLabel, xUnit)
    b = True
    with open(fNameOut, "wt") as g:

        numLine=0
        for x, s_y in x_s_y.iteritems():

            numLine += 1

            line = str(x)

            for s, y in s_y.iteritems():
                line += "," + str(y)

                if b:
                    hLine += "," + str(s)  + "_" + yUnit
            if b:
                print >> g, "{0}".format(hLine)
                b = False

            print >> g, "{0}".format(line)

    return csvFNameOut


def writeCSV_ElapseTime_Obj_heu(lHeu, tw, err, cum = False, xmin = None, xmax = None, cplex =False, lbMachines =None):

    xLabel = "Elapsed-Time"
    xUnit = "hours"

    if cum:
        yLabel = "Total-Run-Time-of-allocated-machines"
        yUnit = "hours"
    else:
        yLabel = "Number-Of-Allocated-Machines"
        yUnit = "unit"

    seriesName = "Heuristic"
    if cplex:
        seriesName += "Cplex"

    if xmin is not None and xmax is not None:
        seriesName +='_peak'
        if xmin is not None:
            seriesName +='_'+str(xmin)
        if xmax is not None :
            seriesName +='_'+str(xmax)


    csvFNameOut = "{0}_{1}_{2}_err{3}_tw{4}.csv".format(xLabel, yLabel, seriesName, err, tw)
    print xLabel, yLabel
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "usage_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict(OrderedDict([])) # x coord, s serie name, y coord


    for h in lHeu:
        if h in CONST_NOPLOT_TW0 and tw == 0: continue
        if tw == 0:
            fName = baseName + str(err) + "_" + h + "_" + "LIST" + "_" + str(2) + ".csv"
        else:
            fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"

        print fName
        with open(fName, "rt") as f:
            totScore = 0
            y1=0
            if lbMachines is not None:
                y1= lbMachines*tw
            for line in f:
                x = float(line.strip().split(", ")[0])/(1000000.0*3600)
                y = float(line.strip().split(", ")[-1])
                if xmin is not None :
                    if x < xmin: continue
                if xmax is not None :
                    if x > xmax: break


                if cum:
                    totScore += (y-y1)
                    y = totScore / 3600.0 # relative cumulative runtime of allocated machines (in hours) till current tw
                else:
                    y = y / float(tw) # number of allocated machine per seconds of the current tw
                if not x in x_s_y:
                    x_s_y.update({x : {h : y}})
                else:
                    x_s_y[x].update({h : y})

    #enriching x_s_y to map each x to a serieName and a value or None
    for x in  x_s_y.keys():
        for h in lHeu:
            if h in CONST_NOPLOT_TW0 and tw == 0: continue
            if h not in x_s_y[x].keys():
                #print x
                #if tw == 0 and h == CONST_H_FMF : continue
                x_s_y[x].update({h : "None"})
        x_s_y[x] =OrderedDict(sorted(x_s_y[x].items(), key=lambda t: t[0]))

    x_s_y = OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))


    hLine = "{0}_{1}".format(xLabel, xUnit)
    b = True
    with open(fNameOut, "wt") as g:

        numLine=0
        for x, s_y in x_s_y.iteritems():

            numLine+=1

            line = str(x)

            for s, y in s_y.iteritems():
                line += "," + str(y)
                if b:
                    hLine += "," + str(s)  + "_" + yUnit
            if b:
                print >> g, "{0}".format(hLine)
                b = False

            print >> g, "{0}".format(line)

    return csvFNameOut



def writeCSV_ElapseTime_SolvingTime_heu( lHeu, tw, err, cum = False,  xmin = None, xmax = None, cplex =False, nbTasksMin = 0.0, tLimit =None):

    xLabel = "Elapsed-Time"
    xUnit = "hours"

    if cum:
        yLabel = "Total-Solving-Time"
        yUnit = "seconds"
    else:
        yLabel = "Solving-Time"
        yUnit = "seconds"

    seriesName = "Heuristics"

    if cplex:
        seriesName += "Cplex"

    if xmin is not None and xmax is not None:
        seriesName +='_peak'
        if xmin is not None:
            seriesName +='_'+str(xmin)
        if xmax is not None :
            seriesName +='_'+str(xmax)

    csvFNameOut = "{0}_{1}_{2}_err{3}_tw{4}.csv".format(xLabel,yLabel,seriesName, err,tw)

    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "time_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict(OrderedDict([])) # x coord, s serie name, y coord


    for h in lHeu:
        if h in CONST_NOPLOT_TW0 and tw == 0: continue
        if tw == 0:
            fName = baseName + str(err) + "_" + h + "_" + "LIST" + "_" + str(2) + ".csv"
        else:
            fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"


        print fName

        fNameLb = "{0}lb_allTasks_U0_myFF_DDUR_{1}.csv".format(baseIn, tw)

        print fNameLb


        with open(fName) as f, open(fNameLb) as fLb:

            totScore = 0
            for line, lineLb in izip(f, fLb):
                y = float(line.strip().split(", ")[-1])
                x = float(line.strip().split(", ")[0])/3600.0

                if tLimit != None:
                    if y > tLimit :
                        y =tLimit-0.01

                nbTasks = int(lineLb.strip().split(", ")[3])
                if nbTasks < nbTasksMin:
                    continue

                if xmin is not None :
                    if x < xmin: continue
                if xmax is not None :
                    if x > xmax: break

                if cum:
                    y +=  totScore
                    totScore = y
                if not x in x_s_y:
                    x_s_y.update({x : {h : y}})
                else:
                    x_s_y[x].update({h : y})



    #enriching x_s_y to map each x to a serieName and a value or None
    for x in  x_s_y.keys():
        for h in lHeu:
            if h in CONST_NOPLOT_TW0 and tw == 0: continue
            if  h not in x_s_y[x].keys():
                x_s_y[x].update({h : "None"})
        x_s_y[x] =OrderedDict(sorted(x_s_y[x].items(), key=lambda t: t[0]))

    x_s_y = OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))


    hLine = "{0}_{1}".format(xLabel, xUnit)
    b = True
    with open(fNameOut, "wt") as g:

        for x, s_y in x_s_y.iteritems():


            line = str(x)

            for s, y in s_y.iteritems():
                line += "," + str(y)

                if b:
                    hLine += "," + str(s)  + "_" + yUnit
            if b:
                print >> g, "{0}".format(hLine)
                b = False

            print >> g, "{0}".format(line)

    return csvFNameOut

def writeCSV_Stat_SolvingTime_heu( lHeu, tw, err, cum = False,  xmin = None, xmax = None, cplex =False, nbTasksMin = 0.0, tLimit =None):

    xLabel = "Stat"
    xUnit = "unit"

    if cum:
        yLabel = "Total-Solving-Time"
        yUnit = "seconds"
    else:
        yLabel = "Solving-Time"
        yUnit = "seconds"

    seriesName = "Heuristics"

    if cplex:
        seriesName += "Cplex"

    if xmin is not None and xmax is not None:
        seriesName +='_peak'
        if xmin is not None:
            seriesName +='_'+str(xmin)
        if xmax is not None :
            seriesName +='_'+str(xmax)

    csvFNameOut = "{0}_{1}_{2}_err{3}_tw{4}.csv".format(xLabel,yLabel,seriesName, err,tw)

    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "time_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict(OrderedDict([])) # x coord, s serie name, y coord


    for h in lHeu:
        if h in CONST_NOPLOT_TW0 and tw == 0: continue
        if tw == 0:
            fName = baseName + str(err) + "_" + h + "_" + "LIST" + "_" + str(2) + ".csv"
        else:
            fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"


        print fName

        fNameLb = "{0}lb_allTasks_U0_myFF_DDUR_{1}.csv".format(baseIn, tw)

        print fNameLb


        with open(fName) as f, open(fNameLb) as fLb:

            totScore = 0
            for line, lineLb in izip(f, fLb):
                y = float(line.strip().split(", ")[-1])
                x = float(line.strip().split(", ")[0])/3600.0

                if tLimit != None:
                    if y > tLimit :
                        y =tLimit

                nbTasks = int(lineLb.strip().split(", ")[3])
                if nbTasks < nbTasksMin:
                    continue

                if xmin is not None :
                    if x < xmin: continue
                if xmax is not None :
                    if x > xmax: break

                if cum:
                    y +=  totScore
                    totScore = y
                if not x in x_s_y:
                    x_s_y.update({x : {h : y}})
                else:
                    x_s_y[x].update({h : y})



    #enriching x_s_y to map each x to a serieName and a value or None
    for x in  x_s_y.keys():
        x_s_y[x] =OrderedDict(sorted(x_s_y[x].items(), key=lambda t: t[0]))

    h_stats = OrderedDict([])
    statMetrics =["mean","max",'median']
    for h in lHeu:
#         h_vals = [y for x,s_y in x_s_y.iteritems()  for s,y in s_y.iteritems() if s==h]
        h_vals =[]
        for x,s_y in x_s_y.iteritems():
            for s,y in s_y.iteritems() :
                if s==h:
                    h_vals.append(y)


        hmean = mean(h_vals)
        hmax = max(h_vals)
        hmed = median(h_vals)

        h_stats.update({h:[hmean,hmax,hmed]})

    h_stats = OrderedDict(sorted(h_stats.items(), key=lambda t: t[0]))


    hLine = "Stats"
    b = True
    with open(fNameOut, "wt") as g:

        for i in range(len(statMetrics)):
            line = statMetrics[i]
            for h, statM in h_stats.iteritems():
                line += ","+str(statM[i])
                if b:
                    hLine += "," + str(h)  + "_" + yUnit


            if b:
                print >> g, "{0}".format(hLine)
                b = False

            print >> g, "{0}".format(line)

    return csvFNameOut



def writeCSV_tw_obj_heu(lTW, lHeu, err,xmin = None, xmax = None, cplex =False):

    xLabel = "Time-Step-Duration"
    xUnit = "secs"

    yLabel = "Run-Time-Of-Allocated-Machines"
    yUnit = "hours"

    seriesName = "Heuristic"
    if cplex:
        seriesName+="Cplex"

    if xmin is not None and xmax is not None:
        seriesName +='_peak'
        if xmin is not None:
            seriesName +='_'+str(xmin)
        if xmax is not None :
            seriesName +='_'+str(xmax)

    csvFNameOut = "{0}_{1}_{2}_err{3}.csv".format(xLabel,yLabel,seriesName, err)
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "usage_allTasks_U"
    ordering = "DDUR"
    x_s_y =OrderedDict(OrderedDict([])) # x coord, s serie name, y coord

    for h in lHeu:
        for x in lTW:
            if h in CONST_NOPLOT_TW0 and x == 0: continue
            if x == 0:
                fName = baseName + str(err) + "_" + h + "_" + "LIST" + "_" + str(2) + ".csv"
            else:
                fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(x) + ".csv"

            print fName

            with open(fName, "rt") as f:

                totScore = 0
                for line in f:
                    ct = float(line.strip().split(", ")[0])/(1000000.0*3600)
                    if xmin is not None :
                        if ct < xmin: continue
                    if xmax is not None :
                            if ct > xmax: break

                    sc = float(line.strip().split(", ")[-1])
                    totScore += sc
            if not x in x_s_y:
                x_s_y.update({x : {h : totScore/3600.0}})
            else:
                x_s_y[x].update({h : totScore/3600.0})


    #enriching x_s_y to map each x to a serieName and a value or None
    for x in  x_s_y.keys():
        for h in lHeu:
            #if h in CONST_NOPLOT_TW0 and x == 0: continue
            if  h not in x_s_y[x].keys():
                x_s_y[x].update({h : "None"})
        x_s_y[x] =OrderedDict(sorted(x_s_y[x].items(), key=lambda t: t[0]))

    x_s_y = OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))


    hLine = "{0}_{1}".format(xLabel, xUnit)
    b = True
    with open(fNameOut, "wt") as g:

        for x, s_y in x_s_y.iteritems():


            line = str(x)

            for h, s in s_y.iteritems():
                line += "," + str(s)

                if b:
                    hLine += "," + str(h)  + "_" + yUnit
            if b:
                print >> g, "{0}".format(hLine)
                b = False

            print >> g, "{0}".format(line)

    return csvFNameOut


def writeCSV_error_obj_heu(lErr, lHeu, tw, cplex= False):

    xLabel = "Task-Duration-Prediction-Error"
    xUnit = "percent"

    yLabel = "Run-Time-Of-Allocated-Machines"
    yUnit = "hours"

    seriesName = "Heuristic"
    if cplex:
        seriesName+="Cplex"

    csvFNameOut = "{0}_{1}_{2}_tw{3}.csv".format(xLabel,yLabel,seriesName, tw)
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "usage_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict(OrderedDict([])) # x coord, s serie name, y coord

    for h in lHeu:
        if tw == 0 and h in CONST_NOPLOT_TW0: continue
        for x in lErr:
            if tw == 0:
                fName = baseName + str(x) + "_" + h + "_" + "LIST" + "_" + str(2) + ".csv"
            else:
                fName = baseName + str(x) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"

            print fName

            with open(fName, "rt") as f:

                totScore = 0
                for line in f:
                    sc = int(line.strip().split(", ")[-1])
                    totScore += sc
            if not x in x_s_y:
                x_s_y.update({x : {h : totScore / 3600.0}})
            else:
                x_s_y[x].update({h : totScore / 3600.0})

    #enriching x_s_y to map each x to a serieName and a value or None
    for x in  x_s_y.keys():
        for h in lHeu:
            if tw == 0 and h in CONST_NOPLOT_TW0: continue
            if h not in x_s_y[x].keys():
                x_s_y[x].update({h : "None"})
        x_s_y[x] =OrderedDict(sorted(x_s_y[x].items(), key=lambda t: t[0]))

    x_s_y = OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))


    hLine = "{0}_{1}".format(xLabel, xUnit)
    b = True
    with open(fNameOut, "wt") as g:

        for x, s_y in x_s_y.iteritems():
            line = str(x)

            for h, s in s_y.iteritems():
                line += "," + str(s)

                if b:
                    hLine += "," + str(h)  + "_" + yUnit
            if b:
                print >> g, "{0}".format(hLine)
                b = False

            print >> g, "{0}".format(line)

    return csvFNameOut

# This is my bit.
def writeCSV_starPlot(lHeu, lErr, lTw):
    # We should produce one CSV per TimeWindow size.
    # The main (top) axis should be a measure of the the objectif function.
    # Right axis; a measure of the robustness
    # Left axis; a measure of the performance of the soving method.

    fol = baseIn
    fOut = "{0}csv/starPlot.csv".format(fol)

    # Getting stats for solving time

    solvTimesAvg = {}
    solvTimesStd = {}
    solvTimesAvgHeu = {}
    solvTimesStdHeu = {}
    solvTimesAvgErrHeu = {}
    solvTimesStdErrHeu = {}


    for h in lHeu:
        for x in lErr:
            for t in lTw:

                solvTimes = {}
                fil = "{0}time_allTasks_U{1}_{2}_DDUR_{3}.csv".format(fol, x, h, t)

                with open(fil, "rt") as f:
                    for l in f:

                        st = float(l.strip().split(", ")[-1]) # Parse the time

                        try:
                            solvTimes[(h, x, t)].append(st)
                        except KeyError:
                            solvTimes[(h, x, t)] = [st]

                # Flatten the lists. Get the avg and std of (h, x, t)
                solvTimesAvg[(h, x, t)] = np.average(solvTimes[(h, x, t)])
                solvTimesStd[(h, x, t)] = np.std(solvTimes[(h, x, t)])

            # Done with all couples(x, t)
            solvTimesAvgErrHeu[(h, x)] = np.average([v for k, v in solvTimesAvg.iteritems() if h in k and x in k])
            solvTimesStdErrHeu[(h, x)] = np.average([v for k, v in solvTimesStd.iteritems() if h in k and x in k])

        solvTimesAvgHeu[h] = np.average([v for k, v in solvTimesAvgErrHeu.iteritems() if h in k])
        solvTimesStdHeu[h] = np.average([v for k, v in solvTimesStdErrHeu.iteritems() if h in k])

    # Get robustness agains prediction errors function.
    robErr = {}
    totObjx000 = {}
    totObjx100 = {}
    robErrHeuTw = {}

    for h in lHeu:
        for t in lTw:

            fil000 = "{0}usage_allTasks_U{1}_{2}_DDUR_{3}.csv".format(fol, 0, h, t)
            fil100 = "{0}usage_allTasks_U{1}_{2}_DDUR_{3}.csv".format(fol, 300, h, t)

            with open(fil000, "rt") as f:
                for l in f:
                    # Parse the obj in bucket
                    obj = float(l.strip().split(", ")[-1])
                    try:
                        totObjx000[(h, t)].append(obj)
                    except KeyError:
                        totObjx000[(h, t)] = [obj]

            with open(fil100, "rt") as f:
                for l in f:
                    # Parse the obj in bucket
                    obj = float(l.strip().split(", ")[-1])
                    try:
                        totObjx100[(h, t)].append(obj)
                    except KeyError:
                        totObjx100[(h, t)] = [obj]

            # We parsed all the local objs. Let's sum em.
            totObjx000[(h, t)] = sum(totObjx000[(h, t)])
            totObjx100[(h, t)] = sum(totObjx100[(h, t)])
            robErrHeuTw[(h, t)] = (totObjx100[(h, t)] - totObjx000[(h, t)]) / float(totObjx000[(h, t)])
            #print "({2}/{3}) - 000 : {0} | 100 : {1} -> {4} ".format(totObjx000[(h, t)], totObjx100[(h, t)], h, t, robErrHeuTw[(h, t)])
        robErr[h] = np.average([v for k, v in robErrHeuTw.iteritems() if h in k])

    # Get how much Heuristics are benifiting from more information (bigger time windows)
    robTW = {}
    robTWHeu = {}
    totObjt002 = {}
    totObjt30 = {}
    tobj = {}

    for h in lHeu:
        for x in lErr:

            fil001 = "{0}usage_allTasks_U{1}_{2}_DDUR_{3}.csv".format(fol, x, h, 2)
            fil120 = "{0}usage_allTasks_U{1}_{2}_DDUR_{3}.csv".format(fol, x, h, 30)

            with open(fil001, "rt") as f:
                for l in f:
                    # Parse the obj in bucket
                    obj = float(l.strip().split(", ")[-1])
                    try:
                        totObjt002[(h, x)].append(obj)
                    except KeyError:
                        totObjt002[(h, x)] = [obj]

            with open(fil120, "rt") as f:
                for l in f:
                    # Parse the obj in bucket
                    obj = float(l.strip().split(", ")[-1])
                    try:
                        totObjt30[(h, x)].append(obj)
                    except KeyError:
                        totObjt30[(h, x)] = [obj]

            totObjt002[(h, x)] = sum(totObjt002[(h, x)])
            totObjt30[(h, x)] = sum(totObjt30[(h, x)])
            robTWHeu[(h, x)] = (totObjt30[(h, x)] - totObjt002[(h, x)]) / float(totObjt30[(h, x)])
        robTW[h] = np.average([v for k, v in robTWHeu.iteritems()   if h in k])
        tobj[h]  = np.average([v for k, v in totObjt002.iteritems() if h in k])

    with open(fOut, "wt") as f:
        print >> f, "heu, t_avg, t_std, Robustness, dObjdTw, Obj"
        for h in lHeu:
            print >> f, "{0}, {1}, {2}, {3}, {4}, {5}".format(h, solvTimesAvgHeu[h] * 1000, solvTimesStdHeu[h], robErr[h] * 100, robTW[h] * 100, tobj[h] / min(tobj[h] for h in lHeu) * 100)
    return fOut


def starPlotFromCSV(csvIn, axesMargin = 0.1):

    data   = {}

    # TODO : Write the parser.
    # data should be a dict from hName to a list of values.

    with open(csvIn, "rt") as f:
        for i, l in enumerate(f):
            if i == 0:
                variables = l.strip().split(", ")[1:]
            else:
                line = l.strip().split(", ")
                data[str(line[0])] = map(float, line[1:])

    print "vars",variables
    print "data",data

    # Find (min, max) for each variables
    # lb and ub might have to be swapped depending wether are not more is better.
    # TODO : Fuck this is broken.

    ranges = []

    for i, var in enumerate(variables):
        print i,var

        # Get lb, get ub, append to ranges.
        if var in [ "A", "B", "C", "D","H"]:
            ranges.append((4900, 8000))
            continue
        if var in [ "E"]:
            ranges.append((35, 60))
            continue
        if var in [ "F","G"]:
            ranges.append((0, 2))
            continue

#         print "No predefined bounds"
#         vals = []
#         for k, v in data.iteritems():
#             vals.append(v[i])
#         print vals
#         lb, ub = min(vals)*(1-axesMargin), max(vals)*(1+axesMargin)
#         ranges.append((lb, ub))


    for i, var in enumerate(variables):
        # The normal case, smaller is better.
        if var in ["t_avg", "t_std", "Robustness", "Obj", "A", "B", "C", "D","E", "F", "G","H"]:
            ranges[i] = (ranges[i][1], ranges[i][0])
        elif var in ["dObjdTw"]:
            ranges[i] = (ranges[i][0], ranges[i][1])
        # The inverse case, smaller is better.
#         else:
#             assert(False), "Unkown variable !"


    fName = "spider_test.pdf"

    pp = PdfPages("{0}{1}".format(baseOutPlot, fName))

    # plotting
    fig = plt.figure() # figsize=(9,9)

    radar = ComplexRadar(fig, variables, ranges)

    handles = []
    labels  = []

    for k, v in data.iteritems():
        #print k, " -> ", v
        x = radar.plot(v)
        radar.fill(v, alpha = 0.2)
        handles.append(x)
        labels.append(k)

    radar.legend(handles, labels)

    pp.savefig(fig)
    pp.close()

relabel = {
        "myFF"  : "FF",
        "FMF" : "FMF",
        "myNF"  : "NF",
        "myBFD" : "BFD",
        "myBFR" : "BFR",
        "myMRD" : "MRD",
        "myMRR" : "MRR",
        "mySS" : "SS",
        "myHA" : "HA",
        "lb"   : "lb",

        "myFF_CPLEX"  : "FF_NS",
        "FMF_CPLEX" : "FMF_NS",
        "myNF_CPLEX"  : "NF_NS",
        "myBFD_CPLEX" : "BFD_NS",
        "myBFR_CPLEX" : "BFR_NS",
        "myMRD_CPLEX" : "MRD_NS",
        "myMRR_CPLEX" : "MRR_NS",
        "mySS_CPLEX" : "SS_NS",
        "myHA_CPLEX" : "HA_NS",

        }

recolor = {
        "myFF"  : "red",
        "FMF" : "blue",
        "myNF"  : "brown",
        "myBFD" : "darkgreen",
        "myBFR" : "seagreen",
        "myMRD" : "purple",
        "myMRR" : "magenta",
        "mySS" : "orange",
        "myHA" : "grey",
        "lb"   : "black",

        "myFF_CPLEX"  : "red",
        "FMF_CPLEX" : "blue",
        "myNF_CPLEX"  : "brown",
        "myBFD_CPLEX" : "darkgreen",
        "myBFR_CPLEX" : "seagreen",
        "myMRD_CPLEX" : "purple",
        "myMRR_CPLEX" : "magenta",
        "mySS_CPLEX" : "orange",
        "myHA_CPLEX" : "grey",


        }


restyle = {
        "FF_DDUR":"FF-D",
        "FMFF_DDUR":"FMF",
        "FF_LIST":"FF-L",
        "FF_DREQ":"FF-R",
        "NF_DDUR":"NF-D",
        "BFD_DDUR":"BFD-D",
        "FMFFTid_DDUR":"FMFT"
        }

rest = {

        "myFF"  : "solid",
        "FMF" : "solid",
        "myNF"  : "solid",
        "myBFD" : "solid",
        "myBFR" : "solid",
        "myMRD" : "solid",
        "myMRR" : "solid",
        "mySS" : "solid",
        "myHA" : "solid",
        "lb"   : "solid",

        "myFF_CPLEX"  : "dashdot",
        "FMF_CPLEX" : "dashdot",
        "myNF_CPLEX"  : "dashdot",
        "myBFD_CPLEX" : "dashdot",
        "myBFR_CPLEX" : "dashdot",
        "MRD_CPLEX" : "dashdot",
        "MFR_CPLEX" : "dashdot",
        "mySS_CPLEX" : "dashdot",
        "myHA_CPLEX" : "dashdot",

        }

m   =   {
        "FF_DDUR"   : '*',
        "FMFF_DDUR" : '+',
        "FF_LIST"   : 'x',
        "FF_DREQ"   : 'd',
        "NF_DDUR"   : '1',
        "BFD_DDUR"  : '2',
        "lb"        : ".",
        "FMFFTid_DDUR":"FMFT"
        }



server ="server_"
baseIn = "../../"+server+"results/uncertain/"
baseInst = "../data/uncertain/"
baseRes = "res"
baseUsage = "usage"
baseSolvingTime = "time"
baseLb = "lb"
baseOutCsv = "../../"+server+"results/uncertain/csv/"
baseInCsvToPlot = "../../"+server+"results/uncertain/csv/"
baseOutPlot = "../../"+server+"results/uncertain/plots/"

if __name__ == '__main__':

    # Experiments parameters
    lErr = [0, 50, 100,150, 200, 250, 300]
    lTw  = [0, 2, 10, 20, 30]
#     lHeu = [
#         CONST_H_FMF,
#         CONST_H_myFF,
#         CONST_H_myBFD,
#         CONST_H_mySS,
# #         CONST_H_myNF,
#         CONST_H_myBFR,
# #         CONST_H_myHA,
#         CONST_H_myMRD,
#         CONST_H_myMRR,
#         ]

    lHeuCplex = [
        CONST_H_FMF_CPLEX,
        CONST_H_myFF_CPLEX,
        CONST_H_myBFD_CPLEX,
        CONST_H_mySS_CPLEX,
#         CONST_H_myNF_CPLEX,
        CONST_H_myBFR_CPLEX,
#         CONST_H_myHA_CPLEX,
        CONST_H_myMRD_CPLEX,
        CONST_H_myMRR_CPLEX
        ]
    lHeu = lHeuCplex



#     # Error vs RunTimeOfAllocatedMachines per Heuristics
#     for tw in lTw:
#         if tw ==2:
#             csvFNameOut = writeCSV_error_obj_heu(lErr, lHeu, tw)
#             plotFromCSV(csvFNameOut,"(tw:{0}secs)".format(tw))

#     # TimeWindow Sizes vs RunTimeOfAllocatedMachines per Heuristics
#     for err in lErr:
#         if err == 0:
#             csvFNameOut = writeCSV_tw_obj_heu(lTw, lHeu, err)
#             plotFromCSV(csvFNameOut,"(err:{0}%)".format(err))

    # ElapsedTime vs SolvingTime per Heuristics
    #for (tw,err) in product(lTw, lErr):
        #csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu(lHeu, tw, err, False, "basicHeuristics")
        #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
        #csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu(lHeu, tw, err, True, "basicHeuristics")
        #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))

        #NOTE : Did not do anything here. LIST for CPLEX is not relevant.
        #NOTE : We should test this with more CPLEX variants.
        #lHeu = [CONST_H_CPLEX,CONST_H_FMF_CPLEX]
        #csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu( lHeu, tw,err,False,"cplexHeuristics")
        #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
        #csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu( lHeu, tw,err,True,"cplexHeuristics")
        #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))

    #ElapsedTime vs  RunTimeOfAllocatedMachines per Heuristics
    for (tw,err) in product(lTw, lErr):
        if tw == 2 and err == 0:
            # Run time of allocated machines per heuristics
            # TOKENHERE
            # xmin, xmax = 123.0833, 124.083  tw =30 zoom <=>  xmin, xmax = 123,124 tw =2
            xmin, xmax = None, None #
#             csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu, tw, err, False, xmin, xmax)
#             plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
            # Cumulative running time of allocated machines per heuristics
            csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu, tw, err, True, xmin, xmax)
            plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))

    #csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu, tw, err)
    #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
    ## Cumulative running time of allocated machines per heuristics
    #csvFNameOut = writeCSV_ElapseTime_Obj_heu(lHeu, tw, err, True)
    #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))


    # ElapsedTime vs  RunTimeOfAllocatedMachines per PredictionError
    #for (h, tw) in product(lHeu, lTw):
        #if h in CONST_NOPLOT_TW0 and tw == 0: continue
        #csvFNameOut = writeCSV_ElapseTime_Obj_err(lErr, h, tw)
        #plotFromCSV(csvFNameOut,"(h:{0},tw:{1}secs)".format(h, tw))
        #csvFNameOut = writeCSV_ElapseTime_Obj_err(lErr, h, tw, True)
        #plotFromCSV(csvFNameOut,"(h:{0},tw:{1}secs)".format(h, tw))

    # ElapsedTime vs  RunTimeOfAllocatedMachines per Time Window

#     for (h, err) in product(lHeu, lErr):
#         if (h == CONST_H_FMF or h == CONST_H_myFF or h == CONST_H_myBFD) and err ==0:
#             #csvFNameOut = writeCSV_ElapseTime_Obj_tw(lTw, h, err, cum = False)
#             #plotFromCSV(csvFNameOut,"(h:{0},err:{1}%)".format(h,err))
#             xMin,xMax = None,None
#             csvFNameOut = writeCSV_ElapseTime_Obj_tw(lTw, h, err, cum = True,xmin=xMin,xmax=xMax)
#             plotFromCSV(csvFNameOut,"(h:{0},err:{1}%)".format(h,err))

    # TimeWindow Sizes vs  RunTimeOfAllocatedMachines per Heuristics
    for err in lErr:
        if err == 0:
            csvFNameOut = writeCSV_tw_obj_heu(lTw, lHeu, err)
            plotFromCSV(csvFNameOut,"(err:{0}%)".format(err))


    # Error vs RunTimeOfAllocatedMachines per Heuristics
    #for tw in lTw:
        #csvFNameOut = writeCSV_error_obj_heu(lErr, lHeu, tw)
        #plotFromCSV(csvFNameOut,"(tw:{0}secs)".format(tw))

    # ElapsedTime vs SolvingTime per Heuristics
    #for (tw,err) in product(lTw, lErr):
        #csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu( lHeu, tw,err,False,"basicHeuristics")
        #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
        #csvFNameOut = writeCSV_ElapseTime_SolvingTime_heu(lHeu, tw, err, True, "basicHeuristics")
        #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err, tw))

        #NOTE : Did not try these CPLEX variants for now.
        #csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu( lHeu, tw,err,False,"cplexHeuristics")
        #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
        #csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu( lHeu, tw,err,True,"cplexHeuristics")
        #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))

    # ElapsedTime vs  RunTimeOfAllocatedMachines per Heuristics

    #for (tw,err) in product(lTw, lErr):
        ## Run time of allocated machines per heuristics
        #csvFNameOut =writeCSV_ElapseTime_Obj_heu(lHeu, tw, err)
        #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err, tw))
        ## Cumulative running time of allocated machines per heuristics
        #csvFNameOut =writeCSV_ElapseTime_Obj_heu(lHeu, tw, err, True)
        #plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err, tw))


    # ElapsedTime vs  RunTimeOfAllocatedMachines per PredictionError
    #for (h,tw) in product(lHeu, lTw):
        #csvFNameOut = writeCSV_ElapseTime_Obj_err(lErr, h, tw)
        #if csvFNameOut != None:
            #plotFromCSV(csvFNameOut,"(h:{0},tw:{1}secs)".format(h, tw))

        #csvFNameOut = writeCSV_ElapseTime_Obj_err(lErr, h, tw, True)
        #if csvFNameOut != None:
            #plotFromCSV(csvFNameOut,"(h:{0},tw:{1}secs)".format(h, tw))
    # NOTE : Here.
    #  ElapsedTime vs RunTimeOfAllocatedMachines per Time Window
    #for (h, err) in product(lHeu, lErr):
        ##csvFNameOut = writeCSV_ElapseTime_Obj_tw(lTw, h, err, cum = False)
        ##plotFromCSV(csvFNameOut,"(h:{0},err:{1}%)".format(h,err))
        #csvFNameOut = writeCSV_ElapseTime_Obj_tw(lTw, h, err, cum = True)
        #plotFromCSV(csvFNameOut,"(h:{0},err:{1}%)".format(h,err))

# ------------------------------------------------------------------------------
# Stats on benchmark
#
#-------------------------------------------------------------------------------
    #for tw in lTw:
        #if tw == 0: continue
        #csvFNameOut = writeCSV_tasksInTime(tw)
        #plotNbTasksIPerBucketInTime(csvFNameOut, tw)
        #plotDistNumTaskInBuck(csvFNameOut, tw)

# ------------------------------------------------------------------------------
# The starplot
# - Probably broken for now.
#-------------------------------------------------------------------------------

    lErr = [0, 50, 100]
    lTw  = [2, 10, 20, 30]

    csvFNameOut = writeCSV_starPlot(lHeu, lErr, lTw)
    #csvFNameOut = "../../server_results/uncertain/csv/starPlot.csv"
    starPlotFromCSV(csvFNameOut, axesMargin = 0.05)
