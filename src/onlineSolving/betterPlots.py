import sys
import os
import random
from collections import OrderedDict
sys.path.append('../heuristics/')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from const import *


from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection

def radar_factory(num_vars, frame='polygon'):
    """Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle' | 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)
    # rotate theta such that the first axis is at the top
    theta += np.pi/2

    def draw_poly_patch(self):
        verts = unit_poly_verts(theta)
        return plt.Polygon(verts, closed=True, edgecolor='k')

    def draw_circle_patch(self):
        # unit circle centered on (0.5, 0.5)
        return plt.Circle((0.5, 0.5), 0.5)

    patch_dict = {'polygon': draw_poly_patch, 'circle': draw_circle_patch}
    if frame not in patch_dict:
        raise ValueError('unknown value for `frame`: %s' % frame)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        # define draw_frame method
        draw_patch = patch_dict[frame]

        def fill(self, *args, **kwargs):
            """Override fill so that line is closed by default"""
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            return self.draw_patch()

        def _gen_axes_spines(self):
            if frame == 'circle':
                return PolarAxes._gen_axes_spines(self)
            # The following is a hack to get the spines (i.e. the axes frame)
            # to draw correctly for a polygon frame.

            # spine_type must be 'left', 'right', 'top', 'bottom', or `circle`.
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            # close off polygon by repeating first vertex
            verts.append(verts[0])
            path = Path(verts)

            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta


def unit_poly_verts(theta):
    """Return vertices of polygon for subplot axes.

    This polygon is circumscribed by a unit circle centered at (0.5, 0.5)
    """
    x0, y0, r = [0.5] * 3
    verts = [(r*np.cos(t) + x0, r*np.sin(t) + y0) for t in theta]
    return verts



def plotFromCSV(csvFName,otherParamsInTitle):
    x_y_s_opt = csvFName.split(".")[0]
    plotFName = baseOutPlot+(x_y_s_opt)+'.pdf'
    print plotFName
    pp = PdfPages(plotFName)

    # Fetch the data
    xLabel = None
    xUnit = None
    yLabel = None
    yUnit = None


    i2col ={}
    col2vals = {}
    with  open(baseInCsvToPlot+csvFName,"rt") as f:
        for l in f:
            if xLabel==None:
                vals =  l.strip().split(",")
                for i in range(len(vals)):
                    if i==0:
                        xLabel = vals[i].split("_")[0]
                        col2vals[xLabel]=[]
                        i2col[i]=xLabel
                        xUnit =  vals[i].split("_")[1]
                    else:
                        serieName = vals[i].split("_")[0]
                        i2col[i]=serieName
                        col2vals[serieName]=[]
                        yUnit = vals[i].split("_")[1]

            else:
                vals = map(float,l.strip().split(","))
                for i in range(len(vals)):
                    col2vals[i2col[i]].append(vals[i])


    fig = plt.figure()

    valXYS= x_y_s_opt.split("_")
    plt.title(" {0} vs {1} per {2} \n {3}".format(valXYS[1],valXYS[0],valXYS[2],otherParamsInTitle))

#     print "xLabel", xLabel
    for k, v in col2vals.iteritems():
#         print k, len(v)
        if k != xLabel:
#             print k
#             print v
#             print xLabel
#             print col2vals[xLabel]
            plt.plot(col2vals[xLabel], v, label=k)


    # Now add the legend with some customizations.
    legend = plt.legend(loc='upper left', shadow=False)

    plt.xlabel("{0} in {1}".format(valXYS[0],xUnit))
    plt.ylabel("{0} in {1}".format(valXYS[1],yUnit))
    pp.savefig(fig)
    pp.close()

def writeCSV_ElapseTime_Obj_tw(lTw, h, err, cum=False):
    xLabel = "ElapseTime"
    xUnit = "secs"

    if cum:
        yLabel = "CumulativeRunTimeOfAllocatedMachines"
        yUnit = "secs"
    else:
        yLabel = "RunTimeOfAllocatedMachines"
        yUnit = "secs"

    seriesName = "TimeWindow"

    csvFNameOut = "{0}_{1}_{2}_h{3}_err{4}.csv".format(xLabel,yLabel,seriesName, h,err)
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "usage_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict([]) # x coord, s serie name, y coord


    for tw in lTw:
        fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"
        print fName
        with open(fName, "rt") as f:
            totScore = 0
            for line in f:
                x = float(line.strip().split(", ")[0])/3600.0
                y = float(line.strip().split(", ")[-1])
                if cum:
                    y +=  totScore
                    totScore =y

                if not x in x_s_y:
                    x_s_y.update({x : {tw : y}})
                else:
                    x_s_y[x].update({tw : y})

    #cleaning x_s_y to keep only x mapping to all the series
#     print "before cleaning", x_s_y
    for x in  x_s_y.keys():
        for tw in lTw:
            if  tw not in x_s_y[x].keys():
                x_s_y.pop(x)
                break
#     print "after cleaning", x_s_y

    OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))

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



def writeCSV_ElapseTime_Obj_err(lErr, h, tw, cum=False):
    xLabel = "ElapseTime"
    xUnit = "secs"

    if cum:
        yLabel = "CumulativeRunTimeOfAllocatedMachines"
        yUnit = "secs"
    else:
        yLabel = "RunTimeOfAllocatedMachines"
        yUnit = "secs"

    seriesName = "PredictionError"

    csvFNameOut = "{0}_{1}_{2}_h{3}_tw{4}.csv".format(xLabel,yLabel,seriesName, h,tw)
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "usage_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict([]) # x coord, s serie name, y coord


    for err in lErr:
        fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"
        print fName
        with open(fName, "rt") as f:
            totScore = 0
            for line in f:
                x = float(line.strip().split(", ")[0])/3600
                y = float(line.strip().split(", ")[-1])
                if cum:
                    y +=  totScore
                    totScore =y

                if not x in x_s_y:
                    x_s_y.update({x : {err : y}})
                else:
                    x_s_y[x].update({err : y})

#     print "before cleaning", x_s_y
    #cleaning x_s_y to keep only x mapping to all the series
    for x in  x_s_y.keys():
        for e in lErr:
            if  e not in x_s_y[x].keys():
                x_s_y.pop(x)
                break
#     print "after cleaning", x_s_y

    OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))

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


def writeCSV_ElapseTime_Obj_heu( lHeu, tw,err,cum=False):
    xLabel = "ElapseTime"
    xUnit = "hours"

    if cum:
        yLabel = "CumulativeRunTimeOfAllocatedMachines"
        yUnit = "secs"
    else:
        yLabel = "RunTimeOfAllocatedMachines"
        yUnit = "secs"

    seriesName = "Heuristic"

    csvFNameOut = "{0}_{1}_{2}_err{3}_tw{4}.csv".format(xLabel,yLabel,seriesName, err,tw)
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "usage_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict([]) # x coord, s serie name, y coord


    for h in lHeu:
        fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"
        print fName
        with open(fName, "rt") as f:
            totScore = 0
            for line in f:
                x = float(line.strip().split(", ")[0])/3600.0
                y = float(line.strip().split(", ")[-1])
                if cum:
                    y +=  totScore
                    totScore =y

                if not x in x_s_y:
                    x_s_y.update({x : {h : y}})
                else:
                    x_s_y[x].update({h : y})

    #cleaning x_s_y to keep only x mapping to all the series
    for x in  x_s_y.keys():
        for h in lHeu:
            if  h not in x_s_y[x].keys():
                x_s_y.pop(x)
                break


    OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))

    hLine = "{0}_{1}".format(xLabel, xUnit)
    b = True
    with open(fNameOut, "wt") as g:

        numLine=0
        for x, s_y in x_s_y.iteritems():

            numLine+=1

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



def writeCSV_ElapseTime_SolvingTime_heu( lHeu, tw, err, cum=False):

    xLabel = "ElapseTime"
    xUnit = "hours"

    yLabel = "SolvingTime"
    yUnit = "secs"

    seriesName = "Heuristic"

    csvFNameOut = "{0}_{1}_{2}_err{3}_tw{4}.csv".format(xLabel,yLabel,seriesName, err,tw)
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "time_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict([]) # x coord, s serie name, y coord

    for h in lHeu:
        fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"
        print fName
        with open(fName, "rt") as f:
            totScore=0
            for line in f:
                y = float(line.strip().split(", ")[-1])
                x = float(line.strip().split(", ")[0])
                if cum:
                    y +=  totScore
                    totScore = y

                if not x in x_s_y:
                    x_s_y.update({x : {h : y}})
                else:
                    x_s_y[x].update({h : y})


    #cleaning x_s_y to keep only x mapping to all the series
    for x in  x_s_y.keys():
        for h in lHeu:
            if  h not in x_s_y[x].keys():
                x_s_y.pop(x)
                break


    OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))

    hLine = "{0}_{1}".format(xLabel, xUnit)
    b = True
    with open(fNameOut, "wt") as g:

        numLine=0
        for x, s_y in x_s_y.iteritems():

            numLine+=1

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


def writeCSV_tw_obj_heu(lTW, lHeu, err):

    xLabel = "TimeWindow"
    xUnit = "secs"

    yLabel = "MachineAllocatedTime"
    yUnit = "hours"

    seriesName = "Heuristic"

    csvFNameOut = "{0}_{1}_{2}_err{3}.csv".format(xLabel,yLabel,seriesName, err)
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "usage_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict([]) # x coord, s serie name, y coord

    for h in lHeu:
        for x in lTW:
            fName = baseName + str(err) + "_" + h + "_" + ordering + "_" + str(x) + ".csv"

            print fName

            with open(fName, "rt") as f:

                totScore = 0
                for line in f:
                    sc = float(line.strip().split(", ")[-1])
                    totScore += sc
            if not x in x_s_y:
                x_s_y.update({x : {h : totScore/3600.0}})
            else:
                x_s_y[x].update({h : totScore/3600.0})
    print x_s_y

    x_s_y =  OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))

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


def writeCSV_error_obj_heu(lErr, lHeu, tw):

    xLabel = "Error"
    xUnit = "percent"

    yLabel = "MachineAllocatedTime"
    yUnit = "hours"

    seriesName = "Heuristic"

    csvFNameOut = "{0}_{1}_{2}_tw{3}.csv".format(xLabel,yLabel,seriesName, tw)
    fNameOut = baseOutCsv + csvFNameOut
    baseName = baseIn + "usage_allTasks_U"
    ordering = "DDUR"
    x_s_y = OrderedDict([]) # x coord, s serie name, y coord

    for h in lHeu:
        for x in lErr:
            fName = baseName + str(x) + "_" + h + "_" + ordering + "_" + str(tw) + ".csv"

            print fName

            with open(fName, "rt") as f:

                totScore = 0
                for line in f:
                    sc = int(line.strip().split(", ")[-1])
                    totScore += sc
            if not x in x_s_y:
                x_s_y.update({x : {h : totScore/3600.0}})
            else:
                x_s_y[x].update({h : totScore/3600.0})
    print x_s_y

    x_s_y =  OrderedDict(sorted(x_s_y.items(), key=lambda t: t[0]))

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

# TODO : ElapsedTime vs  NbTasks from lb files
# Left axis  : Should be incoming number of tasks
# and number of runing tasks in the simulator.
# Right axis : Cumulated 
def writeCSV_tasksInTime(tw):
    
    fOut = "{0}csv/numTasksInTime_tw{1}.csv".format(baseIn, tw)
    fIn  = "{0}lb_allTasks_U0_FF_DDUR_{1}.csv".format(baseIn, tw)
    #print fOut
    #assert(False)
    # Getting the number of tasks in a buckets
    # Here's the format for the lower bound file :
    # ct, nct, lb, nTasksInBuck, nTasksInSim    
    
    with open(fIn, "rt") as f:
        
        with open(fOut, "wt") as g:
            print >> g, "ct, nct, nBuckTasks, cnBuckTasks, nSimTasks, cnSimTasks"
            
        nBuckTasks = cnBuckTasks = nSimTasks = cnSimTasks = 0
        
        for l in f:
            line = map(int, map(float, l.strip().split(", ")))
            
            cTime  = line[0]
            ncTime = line[1]
            nBuckTasks = line[3]
            
            # TODO : FIX the missing nSimTasks
            nSimTasks = line[4]
            #nSimTasks  = 0
           
            cnBuckTasks += nBuckTasks
            cnSimTasks  += nSimTasks
            
            with open(fOut, "at") as g:
                print >> g, "{0}, {1}, {2}, {3}, {4}, {5}".format(cTime, ncTime, nBuckTasks, cnBuckTasks, nSimTasks, cnSimTasks)
    
    return fOut

def cpudist(fIn):
    cpus = []

    plotFName = "{0}cpuDist.pdf".format(baseOutPlot)
    pp = PdfPages(plotFName)
    fig, ax1 = plt.subplots()
    with open(fIn, "rt") as f:
        for l in f:
            li = float(l.strip().split(", ")[2])
            ts = int(l.strip().split(", ")[0])
            if ts > 7 * 24 * 3600 * CONST_SECINMILISEC:
                break
            cpus.append(li)
            
    #print cpus
    #print np.average(cpus)
    plt.hist(cpus)
    plt.title("Distribution of cpus")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    
    plt.tight_layout()
    pp.savefig(fig)
    pp.close()    
    
def durdist(fIn):
    durs = []

    plotFName = "{0}durDist.pdf".format(baseOutPlot)
    pp = PdfPages(plotFName)
    fig, ax1 = plt.subplots()
    with open(fIn, "rt") as f:
        for l in f:            
            li = int(l.strip().split(", ")[4])
            ts= int(l.strip().split(", ")[0])
            if ts > 7 * 24 * 3600 * CONST_SECINMILISEC:
                break
            if li < 0.00:
                print li
            else:
                durs.append(li)
                
    # 

    tg = plt.hist(durs, bins = 25)
    
    plt.title("Distribution of durs")
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    
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
                nTasskPerTW.append(line[2])
                #cumTasks.append(line[3])
                #tInSys.append(line[4])
    
    
    tg = plt.hist(nTasskPerTW, bins = 25)
    
    plt.title("Distribution of the number of tasks per bucket of {0} seconds".format(tw))
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    
    plt.tight_layout()
    pp.savefig(fig)
    pp.close()   


def plot_tasksInTime(fIn, tw):
    
    # baseOutPlot
    plotFName = "{0}tasksPerBucket_tw{1}.pdf".format(baseOutPlot, tw)
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
    plt.title("Number of tasks in buckets of {0} seconds over time.".format(tw))
    
    fts = min(time)
    lts = max(time)
    
    
    span = lts - fts
    labs = [i / 3600 / 24  for i in xrange(span) if i % (3600 * 24) == 0]
    pos = [i for i in xrange(span) if i % (3600 * 24) == 0]
    print labs
    
    #print span / 3600.0
    #print 9 * 24
    plt.xticks(pos, labs)    
    
    legend = plt.legend(loc='upper left', shadow=False)

    plt.xlabel("Time in days")
    plt.ylabel("Number of incoming tasks per bucket")
    
    
    plt.plot(time, nTasskPerTW)
    #plt.plot(time, tInSys, 'o')
    
    
    ax2 = ax1.twinx()
    plt.ylabel("Cumulative number of tasks")
    plt.plot(time, cumTasks[1:], linestyle='--', color='r')
    #ax2.set_ylabel('sin', color='r')
    #ax2.tick_params('y', colors='r')
    
    plt.tight_layout()
    pp.savefig(fig)
    pp.close()    
    

# TODO : NbTasks vs solving time per heuristics
# TODO : 

# This is my bit.
def writeCSV_starPlot(lHeu, lErr, lTw):
    # We should produce one CSV per TimeWindow size.
    # The main (top) axis should be a measure of the the objectif function.
    # Right axis; a measure of the robustness
    # Left axis; a measure of the performance of the soving method.

    fol = "../../results/uncertain/"
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
            fil100 = "{0}usage_allTasks_U{1}_{2}_DDUR_{3}.csv".format(fol, 100, h, t)

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
    totObjt001 = {}
    totObjt120 = {}

    for h in lHeu:
        for x in lErr:

            fil001 = "{0}usage_allTasks_U{1}_{2}_DDUR_{3}.csv".format(fol, x, h, 1)
            fil120 = "{0}usage_allTasks_U{1}_{2}_DDUR_{3}.csv".format(fol, x, h, 120)

            with open(fil001, "rt") as f:
                for l in f:
                    # Parse the obj in bucket
                    obj = float(l.strip().split(", ")[-1])
                    try:
                        totObjt001[(h, x)].append(obj)
                    except KeyError:
                        totObjt001[(h, x)] = [obj]

            with open(fil100, "rt") as f:
                for l in f:
                    # Parse the obj in bucket
                    obj = float(l.strip().split(", ")[-1])
                    try:
                        totObjt120[(h, x)].append(obj)
                    except KeyError:
                        totObjt120[(h, x)] = [obj]

            totObjt001[(h, x)] = sum(totObjt001[(h, x)])
            totObjt120[(h, x)] = sum(totObjt120[(h, x)])
            robTWHeu[(h, x)] = (totObjt120[(h, x)] - totObjt001[(h, x)]) / float(totObjt120[(h, x)])
        robTW[h] = np.average([v for k, v in robTWHeu.iteritems() if h in k])


    # Get something about the objective functions
    objt = {}
    for h in lHeu:
        objt[h] = 0.0

    with open(fOut, "wt") as f:
        print >> f, "heu, avgStime, stdSolveTime, robAgainstErr, robTW, obj?"
        for h in lHeu:
            print >> f, "{0}, {1}, {2}, {3}, {4}, {5}".format(h, solvTimesAvgHeu[h], solvTimesStdHeu[h], robErr[h], robTW[h], objt[h])
    return fOut


def starPlotFromCSV(csvIn):

    data = []
    labels = []

    with open(csvIn, "rt") as f:
        for i, l in enumerate(f):
            if i == 0:
                data.append(l.strip().split(", ")[1:])
                data.append(("", []))
            else:
                line = l.strip().split(", ")
                labels.append(line[0])
                data[1][1].append(map(float, line[1:]))

    spoke_labels = data.pop(0)
    N = len(spoke_labels)


    theta = radar_factory(N, frame='polygon')
    fig = plt.figure(figsize=(9, 9))
    fig.subplots_adjust(wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)

    colors = ['b', 'r', 'g', 'm']

    for d in data:
        print d
    n = 0
    title = data[0][0]
    case_data = data[0][1]

    ax = fig.add_subplot(1, 1, 1, projection='radar')
    plt.rgrids([0.5 * (i + 1) for i in range(10)])

    ax.set_title(title, weight='bold', size='medium', position=(0.5, 1.1), horizontalalignment='center', verticalalignment='center')
    for d, color in zip(case_data, colors):
        ax.plot(theta, d, color=color)
        ax.fill(theta, d, facecolor=color, alpha=0.25)
    ax.set_varlabels(spoke_labels)

    legend = plt.legend(labels, loc=(0.9, .95), labelspacing=0.1)
    plt.setp(legend.get_texts(), fontsize='small')

    plt.figtext(0.5, 0.965, 'Comparing profiles of policies',
                ha='center', color='black', weight='bold', size='large')
    plt.show()

    return None





baseIn = "../../results/uncertain/"
baseInst = "../data/uncertain/"

baseRes   = "res"
baseUsage = "usage"
baseSolvingTime = "time"
baseLb = "lb"

baseOutCsv = "../../results/uncertain/csv/"
baseInCsvToPlot = "../../results/uncertain/csv/"
baseOutPlot = "../../results/uncertain/plots/"

if __name__ == '__main__':

    lErr = [0, 10, 30, 40, 60, 80, 100]#[0,10,30,60,80,100]
    lHeu = [CONST_H_FF, CONST_H_CPLEX, CONST_H_BFD, CONST_H_FMF]
    #lTw  = [1, 5, 10, 30, 60, 120]
    #lTw  = [1, 2, 5, 10, 30, 60, 120, 300]
    lTw  = [120]

#     for tw in lTw:
#         csvFNameOut = writeCSV_error_obj_heu(lErr, lHeu, tw)
#         plotFromCSV(csvFNameOut,"(tw:{0}secs)".format(tw))
#
#     for err in lErr:
#         csvFNameOut = writeCSV_tw_obj_heu(lTw, lHeu, err)
#         plotFromCSV(csvFNameOut,"(err:{0}%)".format(err))
#
#
#     for tw in lTw:
#         for err in lErr:
#             csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu( lHeu, tw,err)
#             plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
#             csvFNameOut =writeCSV_ElapseTime_SolvingTime_heu( lHeu, tw,err,True)
#             plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
# #
#     for tw in lTw:
#         for err in lErr:
#             # Run time of allocated machines per heristics
#             csvFNameOut =writeCSV_ElapseTime_Obj_heu( lHeu, tw,err)
#             plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
#             # Cumulative running time of allocated machines per heristics
#             csvFNameOut =writeCSV_ElapseTime_Obj_heu( lHeu, tw,err,True)
#             plotFromCSV(csvFNameOut,"(err={0}%,tw={1}secs)".format(err,tw))
#
#
#     for h in lHeu:
#         for tw in lTw:
#             csvFNameOut = writeCSV_ElapseTime_Obj_err(lErr, h, tw)
#             plotFromCSV(csvFNameOut,"(h:{0},tw:{1}secs)".format(h,tw))
#             csvFNameOut = writeCSV_ElapseTime_Obj_err(lErr, h, tw,True)
#             plotFromCSV(csvFNameOut,"(h:{0},tw:{1}secs)".format(h,tw))
#
#     for h in lHeu:
#         for err in lErr:
#             csvFNameOut = writeCSV_ElapseTime_Obj_tw(lTw, h, err)
#             plotFromCSV(csvFNameOut,"(h:{0},err:{1}%)".format(h,err))
    
    for tw in lTw:
        csvFNameOut = writeCSV_tasksInTime(tw)
        plot_tasksInTime(csvFNameOut, tw)
        plotDistNumTaskInBuck(csvFNameOut, tw)
        
    cpudist("../data/allTasks.csv")
    durdist("../data/allTasks.csv")
#
#    csvFNameOut = writeCSV_starPlot(lHeu, lErr, lTw)
#    starPlotFromCSV(csvFNameOut)   
