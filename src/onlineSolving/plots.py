import sys
import os
import random
sys.path.append('../heuristics/')

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

baseIn = "../../results/googleReal/"
baseInst = "../data/googleReal/"

baseRes = "res"
baseUsage = "usage"
baseSolvingTime = "time"
baseLb = "lb"

def plotCumSolvTime(lines, instName):

    fig = plt.figure()
    plt.title('Instance {0}'.format(instName))

    for k, v in lines.iteritems():
        if k != "tps":
            plt.plot(lines["tps"], v, label=k)


    # Now add the legend with some customizations.
    legend = plt.legend(loc='upper left', shadow=True)

    ### Plotting arrangements ###
    return fig


def plotCumSolvingTimes(hToPlot, bucketSize, instToPlot):
    pp = PdfPages('cumSolvTime.pdf')

    for instName in instToPlot:
        lines = {}
        for h in hToPlot:
            lines["{0}".format(h)] = [0.0]
        print instName
        # Fetch the data
        for k in lines.keys():
            with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseSolvingTime, instName, k, bucketSize), "rt") as f:
                for l in f:
                    lines[k].append(lines[k][-1] + float(l.split(", ")[4]))

        lines["tps"] = [i for i in range(len(lines[hToPlot[0]]))]

        fig = plotCumSolvTime(lines, instName)
        pp.savefig(fig)

    pp.close()




def plotAllocatedSpace(hToPlot, bucketSize, instToPlot):

    pp = PdfPages('{0}allocatedSpace_{1}.pdf'.format(plotTo, instToPlot[0]))

    #print '{0}'.format({0}allocatedSpace_{1}.pdf.format(plotTo, instToPlot[0])

    for instName in instToPlot:
        lines = {}
        for h in hToPlot:
            lines["{0}".format(h)] = []

        # Fetch the data
        for k in lines.keys():
            with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseUsage, instName, k, bucketSize), "rt") as f:
                for l in f:
                    lines[k].append(float(l.split(", ")[3]))

        # Need the lower and time points at this stage
        with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseLb, instName, "FF_DDUR", bucketSize), "rt") as f:
            lines["lb"] = []
            for l in f:
                lines["lb"].append(float(l.split(", ")[2]))

        lines["tps"] = [i for i in range(len(lines["lb"]))]

        fig = plotLbVSMethods(lines, instName)
        pp.savefig(fig)

    pp.close()

def plotLbVSMethods(lines, instName):

    fig = plt.figure()
    #plt.title('Instance {0}'.format(instName))

    for k, v in lines.iteritems():
        if k != "tps":
            print k, " tps:",len(lines["tps"])," v:" ,len(v)
            #plt.set_markersize(500)
            if k == "FMFF_DDUR":
                plt.plot(lines["tps"][400:1400], v[400:1400], label=relabels[k], c = recolor[k], ls=rest[k], marker= m[k], markevery = 15 ,  lw = 0.5, markersize = 10)
            else:
                plt.plot(lines["tps"][400:1400], v[400:1400], label=relabels[k], c = recolor[k], ls=rest[k], marker= m[k], markevery = 15 ,  lw = 0.5, markersize = 5)
            #plt.plot(lines["tps"][400:1400], v[400:1400], label=relabels[k], c = recolor[k], ls=rest[k], marker= m[k],  markevery = 15,  lw = 0.5)
            #print lines["tps"]

    plt.xlabel('Time in seconds')
    plt.ylabel('Number of allocated machines')
    plt.xticks(range(400, 1401, 200), [800 + (i * 400) for i in range(7)])
    plt.yticks(range(0, 1601, 200), range(0, 801, 100))

    # Now add the legend with some customizations.
    legend = plt.legend(loc='upper left', prop={'size':10})

    ### Plotting arrangements ###
    return fig

def plotnMachines(lines, instName):

    fig = plt.figure()
    #plt.title('Instance {0}'.format(instName))

    for k, v in lines.iteritems():
        if k != "tps":
            print k, len(v), len(lines["tps"])
            if k == "FMFF_DDUR":
                plt.plot(lines["tps"], v, label=relabels[k], c = recolor[k], ls=rest[k], marker= m[k], markevery = 15 * 50,  lw = 0.5, markersize = 10)
            else:
                plt.plot(lines["tps"], v, label=relabels[k], c = recolor[k], ls=rest[k], marker= m[k], markevery = 15 * 50,  lw = 0.5, markersize = 5)


    # Now add the legend with some customizations.
    legend = plt.legend(loc='upper left')
    plt.xlabel('Time in hours')
    plt.ylabel('Cumulated allocated CPU time in seconds')

    plt.xticks(range(0, 45001, 3600), [i * 2 for i in range(13)])


    ### Plotting arrangements ###
    return fig

def plotGap(lines, instName):

    fig = plt.figure()
    plt.title('Instance {0}'.format(instName))

    for k, v in lines.iteritems():
        if k != "tps":
            #print k, len(v), len(lines["tps"])
            plt.plot(lines["tps"][100:], v[100:], label=relabels[k], c = recolor[k], ls='-', lw = 0.5)

    plt.ylim([0,2.0])
    # Now add the legend with some customizations.
    legend = plt.legend(loc='upper left')

    ### Plotting arrangements ###
    return fig

def plotCumGap(lines, instName):

    fig = plt.figure()
    #plt.title('Instance {0}'.format(instName))

    for k, v in lines.iteritems():
        if k != "tps":
            #print k, len(v), len(lines["tps"])
            plt.plot(lines["tps"], v, label=relabels[k], c = recolor[k], ls=rest[k], lw = 3.3)

    #plt.ylim([0,2.0])
    # Now add the legend with some customizations.
    plt.xlabel('Time in hours')
    plt.ylabel('Cumulated gap to lower bound in seconds')
    plt.xticks(range(0, 45001, 3600), [i * 2 for i in range(13)])

    #plt.yticks(range(0, 160000000, 3600 * 24), [i  for i in range(10)])


    legend = plt.legend(loc='upper left')

    ### Plotting arrangements
    ###
    return fig

def plotBox(lines, instName):

    fig = plt.figure()
    #plt.title('Distribution of solving times - Instance {0}'.format(instName))

    #for k, v in lines.iteritems():
        #if k != "tps" and != "lb":
    #plt.plot(lines["tps"], v, label=k)
    data = []
    labs = []
    for k in lines.keys():
        if k != "lb" and k != "tps":
            labs.append(relabels[k])
            data.append([t for t in lines[k] if t > 0.001])

    bp = plt.boxplot(data)

    plt.ylabel('Solving Time in seconds')
    plt.setp(bp['boxes'], color='black')
    plt.setp(bp['whiskers'], color='black')
    plt.setp(bp['fliers'], color='red', marker='+')


    locations = range(1, len(labs) + 1)
    plt.xticks(locations, labs)     # rotate the labels
    plt.subplots_adjust(bottom=0.07, left=0.10 )

    # Now add the legend with some customizations.
    legend = plt.legend(loc='upper left')

    ### Plotting arrangements ###
    return fig


def plotBoxTimes(hToPlot, bucketSize, instToPlot):

    pp = PdfPages('{0}boxSolvingTimes_{1}_new.pdf'.format(plotTo, instToPlot[0]))

    for instName in instToPlot:
        lines = {}
        for h in hToPlot:
            lines["{0}".format(h)] = []

        # Fetch the data
        for k in lines.keys():
            with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseSolvingTime, instName, k, bucketSize), "rt") as f:
                for l in f:
                    val = float(l.split(", ")[4])
                    lines[k].append(val)


        lines["tps"] = [i for i in range(len(lines[hToPlot[0]]))]
        for k in lines:
            print "{0} -> {1}".format(k, len([v for v in lines[k] if v > 2.0 ]))

        fig = plotBox(lines, instName)
        pp.savefig(fig)

    pp.close()


def plotSolvTime(lines, instName):

    #fig = plt.figure()
    fig, axarr = plt.subplots(len(lines.keys()) - 1, sharex=True)

    #plt.title('Instance {0}'.format(instName))

    box = 0

    for k, v in lines.iteritems():
        if k != "tps":
            y_pos = np.arange(len(lines["tps"]))
            axarr[box].bar(y_pos, v, label=k, width=2)
            axarr[box].set_autoscaley_on(False)
            axarr[box].set_xlim([0,len(lines["tps"])])
            axarr[box].axhline(y=2.0, xmin=min(lines["tps"]), xmax=max(lines["tps"]), linewidth = 1, color = 'k', ls = "dotted")
            axarr[box].set_yticks(np.arange(0.0, max(v)+0.5, 0.5))
            axarr[box].legend(loc='upper left', shadow=False)
            box += 1

    # Now add the legend with some customizations.
    #legend = plt.legend(loc='upper left')

    return fig



def plotSolvingTimes(hToPlot, bucketSize, instToPlot):
    pp = PdfPages('solvingTimes.pdf')

    for instName in instToPlot:
        lines = {}
        #print "DEB {0} A".format(instName)
        for h in hToPlot:
            lines["{0}".format(h)] = []

        # Fetch the data
        for k in lines.keys():
            with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseSolvingTime, instName, k, bucketSize), "rt") as f:
                for l in f:
                    lines[k].append(float(l.split(", ")[4]))


        lines["tps"] = [i for i in range(len(lines[hToPlot[0]]))]
        fig = plotSolvTime(lines, instName)
        #print "DEB {0} B".format(instName)
        pp.savefig(fig)

    pp.close()

def plotCumAllocatedSpace(hToPlot, bucketSize, instToPlot):

    pp = PdfPages('{0}cumAllocatedSpace{1}.pdf'.format(plotTo, instToPlot[0]))

    for instName in instToPlot:
        lines = {}
        for h in hToPlot:
            lines["{0}".format(h)] = [0.0]

        # Fetch the data
        for k in lines.keys():
            with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseUsage, instName, k, bucketSize), "rt") as f:
                for l in f:
                    lines[k].append(lines[k][-1] + int(float(l.split(", ")[3])))

        # Need the lower and time points at this stage
        with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseLb, instName, "FF_DDUR", bucketSize), "rt") as f:
            lines["lb"] = [0.0]
            for l in f:
                lines["lb"].append(lines["lb"][-1] + float(l.split(", ")[2]))

        lines["tps"] = [i for i in range(len(lines["lb"]))]

        for k in lines:
            print "{0} - > {1}".format(k, lines[k][-1])
        print

        fig = plotnMachines(lines, instName)
        pp.savefig(fig)

    pp.close()


def plotNumMachine(hToPlot, bucketSize, instToPlot):

    pp = PdfPages('allocatedMachines.pdf')

    for instName in instToPlot:
        lines = {}
        for h in hToPlot:
            lines["{0}".format(h)] = []

        # Fetch the data
        for k in lines.keys():
            with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseUsage, instName, k, bucketSize), "rt") as f:
                for l in f:
                    lines[k].append(int(float(l.split(", ")[2])))

        # Need the lower and time points at this stage
        with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseLb, instName, "FF_DDUR", bucketSize), "rt") as f:
            lines["lb"] = []
            for l in f:
                lines["lb"].append(float(l.split(", ")[2]) /float(bucketSize))

        lines["tps"] = [i for i in range(len(lines["lb"]))]

        fig = plotnMachines(lines, instName)
        pp.savefig(fig)

    pp.close()

def plotGapToLb(hToPlot, bucketSize, instToPlot):
    pp = PdfPages('{0}gapToLB{1}.pdf'.format(plotTo, instToPlot[0]))

    for instName in instToPlot:
        lines = {}
        for h in hToPlot:
            lines["{0}".format(h)] = []

        # Get the lb
        with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseLb, instName, "FF_DDUR", bucketSize), "rt") as f:
            lines["lb"] = []
            for l in f:
                lines["lb"].append(float(l.split(", ")[2]))

        # Fetch the data
        for k in lines.keys():
            if k != "lb":
                with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseUsage, instName, k, bucketSize), "rt") as f:
                    cpt = 0
                    for l in f:
                        x = float(l.split(", ")[3])
                        print k
                        lb = lines["lb"][cpt]
                        gapToLb = abs((x - lb) / float(lb))
                        lines[k].append(gapToLb)
                        cpt += 1

        lines["tps"] = [i for i in range(len(lines["lb"]))]
        lines.pop("lb", None)
        print "Last gap to lb"
        for k in lines:
            print "{0} - {1}".format(k, lines[k][-1])

        #fig = plotGap(lines, instName)
        #pp.savefig(fig)

    pp.close()

def plotCumGapToLb(hToPlot, bucketSize, instToPlot, norm = False):
    pp = PdfPages('{0}cumGapToLB{1}.pdf'.format(plotTo, instToPlot[0]))
    print '{0}cumGapToLB{1}.pdf'.format(plotTo, instToPlot[0])
    for instName in instToPlot:
        lines = {}
        for h in hToPlot:
            lines["{0}".format(h)] = [0.0]

        # Get the lb
        with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseLb, instName, "FF_DDUR", bucketSize), "rt") as f:
            lines["lb"] = []
            for l in f:
                lines["lb"].append(float(l.split(", ")[2]))

        # Fetch the data
        for k in lines.keys():
            if k != "lb":
                with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseUsage, instName, k, bucketSize), "rt") as f:
                    cpt = 0
                    for l in f:
                        x = float(l.split(", ")[3])
                        lb = lines["lb"][cpt]
                        gapToLb = abs((x - lb))
                        lines[k].append(lines[k][-1] + gapToLb)
                        cpt += 1

        lines["tps"] = [i for i in range(len(lines["lb"]) +1)]
        lines.pop("lb", None)

        if norm == True:
            m = 0
            for k in lines.keys():
                m = max(m, max(lines[k]))
            for k in lines.keys():
                for i in range(lines[k]):
                    lines[k][i] = lines[k][i] / float(m)

        for k in lines:
            print "{0} -> {1}".format(k, lines[k][-1])

        fig = plotCumGap(lines, instName)
        pp.savefig(fig)

    pp.close()

def plotCumNormGapToLb(hToPlot, bucketSize, instToPlot):
    pp = PdfPages('normCumGapToLB.pdf')

    for instName in instToPlot:
        lines = {}
        for h in hToPlot:
            lines["{0}".format(h)] = []

        # Get the lb
        with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseLb, instName, "FF_DDUR", bucketSize), "rt") as f:
            lines["lb"] = []
            for l in f:
                lines["lb"].append(float(l.split(", ")[2]))

        # Fetch the data
        for k in lines.keys():
            if k != "lb":
                with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseUsage, instName, k, bucketSize), "rt") as f:
                    for l in f:
                        lines[k].append(float(l.split(", ")[3]))


        maxx = []
        for i in range(len(lines["lb"])):
            m = 0
            for k in lines.keys():
                v = lines[k][i]
                print v - lines["lb"][i]
                if (v - lines["lb"][i]) > m:
                    m = v - lines["lb"][i]
            print m
            maxx.append(m)
        m = max(maxx)


        for k in lines.keys():
            if k != "lb":
                cpt = 0
                for i in range(len(lines["lb"])):
                    lines[k][i] = (lines[k][i] - lines["lb"][i]) / float(m)
                    cpt += 1


        lines["tps"] = [i for i in range(len(lines["lb"]))]
        lines.pop("lb", None)

        fig = plotnMachines(lines, instName)
        pp.savefig(fig)

    pp.close()


def plotNormGapToLb(hToPlot, bucketSize, instToPlot):
    pp = PdfPages('normGapToLB.pdf')

    for instName in instToPlot:
        lines = {}
        for h in hToPlot:
            lines["{0}".format(h)] = []

        # Get the lb
        with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseLb, instName, "FF_DDUR", bucketSize), "rt") as f:
            lines["lb"] = []
            for l in f:
                lines["lb"].append(float(l.split(", ")[2]))

        # Fetch the data
        for k in lines.keys():
            if k != "lb":
                with open("{0}{1}_hour{2}_{3}_{4}.csv".format(baseIn, baseUsage, instName, k, bucketSize), "rt") as f:
                    for l in f:
                        lines[k].append(float(l.split(", ")[3]))


        maxx = []
        for i in range(len(lines["lb"])):
            m = 0
            for k in lines.keys():
                v = lines[k][i]
                print v - lines["lb"][i]
                if (v - lines["lb"][i]) > m:
                    m = v - lines["lb"][i]
            print m
            maxx.append(m)
        m = max(maxx)


        for k in lines.keys():
            if k != "lb":
                cpt = 0
                for i in range(len(lines["lb"])):
                    lines[k][i] = (lines[k][i] - lines["lb"][i]) / float(m)
                    cpt += 1


        lines["tps"] = [i for i in range(len(lines["lb"]))]
        lines.pop("lb", None)

        fig = plotnMachines(lines, instName)
        pp.savefig(fig)

    pp.close()



def getdurations(nunInst):
    durs = []
    path = "../data/googleReal/hour{0}.csv".format(nunInst)
    with open(path, "rt") as f:
        for line in f:
            line = line.strip().split(", ")
            d = int(line[4])
            durs.append(d)
    return durs

def getReqs(nunInst):
    reqs = []
    path = "../data/googleReal/hour{0}.csv".format(nunInst)
    with open(path, "rt") as f:
        for line in f:
            line = line.strip().split(", ")
            r = float(line[2])
            reqs.append(r)
    return reqs

def plotDistDur(data, instName):
    fig = plt.figure()
    plt.title('Instance {0}'.format(instName))


    plt.hist(data, bins=100, normed=True)

    # Now add the legend with some customizations.
    #legend = plt.legend(loc='upper left', shadow=True)

    ### Plotting arrangements ###
    return fig

def plotDistReq(data, instName):
    fig = plt.figure()
    plt.title('Instance {0}'.format(instName))


    plt.hist(data, bins=100, normed=True)

    # Now add the legend with some customizations.
    #legend = plt.legend(loc='upper left', shadow=True)

    ### Plotting arrangements ###
    return fig


def plotDistDurationAll(bucketSize, instToPlot):
    pp = PdfPages('durationDistribution.pdf')

    for i in instToPlot:
        # Get the duration
        durs = getdurations(i)

        fig = plotDistDur(durs, i)
        pp.savefig(fig)

    pp.close()

    return

def plotFreqInTime():
    # Get the tasks
    fName = "../data/instAll.csv"
    tasks = []
    with open(fName, "rt") as f:
        for l in f:
            l = l.strip().split(", ")
            tasks.append([int(l[0]), int(float(l[4]))])
    test = plt.hist([a[0] for a in tasks], bins=24 * 60)
    print test
    plt.show()

def plotFreqInTimeOnHour():
    # Get the tasks
    fName = "../data/googleReal/hour10.csv"
    tasks = []

    #beg = 32414092605 + 800 * 1000000
    beg = 32414092605 + 800 * 1000000
    #end = beg + 2000 * 1000000
    end = beg + 2000 * 1000000

    with open(fName, "rt") as f:
        for l in f:
            l = l.strip().split(", ")
            #print beg, end, int(l[0])
            if int(l[0]) >= beg and int(l[0]) <= end:
                tasks.append([int(l[0]), int(float(l[4]))])
                #if int(l[0]) < beg + beg * 0.1:
                    #print "stuff"

    #assert(False)
    # , bins=10
    binwidth = 2 * 1000000
    n, bins, patches = plt.hist([a[0] for a in tasks], bins=range(min([a[0] for a in tasks]), max([a[0] for a in tasks]) + binwidth, binwidth))

    pos  = [beg + i * 1000000 * 400 for i in range(0,6)]
    labs = ["800", "1200","1600","2000","2400","2800"]
    plt.xticks(pos, labs)

    plt.xlabel('Time in seconds')
    plt.ylabel('Number of new tasks arriving')
    #plt.yscale('log', nonposy='clip')


    #print test
    plt.show()


def plotDistReqsAll(bucketSize, instToPlot):
    pp = PdfPages('reqsDistribution.pdf')

    for i in instToPlot:
        # Get the duration
        reqs = getReqs(i)

        fig = plotDistReq(reqs, i)
        pp.savefig(fig)

    pp.close()

# Globals
#plotTo = "../../plots/all/"
plotTo = "./"

relabels ={"FF_DDUR":"FF-D",
               "FMF_DDUR":"FMF",
               "FF_LIST":"FF-L",
               "FF_DREQ":"FF-R",
               "NF_DDUR":"NF-D",
               "BFD_DDUR":"BFD-D",
               "FMFF_DDUR":"FMF",
               "lb":"lb",
               "FMFFTid_DDUR":"FMFT"
               }

recolor = {"FF_DDUR" : "blue",
           "FMFF_DDUR": "red" ,
           "FF_LIST" : "green",
           "FF_DREQ" : "cyan",
           "NF_DDUR" : "magenta",
           "BFD_DDUR": "orange",
           "lb" : "black",
           "FMFFTid_DDUR":"green"
           }

restyle = {"FF_DDUR":"FF-D",
               "FMFF_DDUR":"FMF",
               "FF_LIST":"FF-L",
               "FF_DREQ":"FF-R",
               "NF_DDUR":"NF-D",
               "BFD_DDUR":"BFD-D",
               "FMFFTid_DDUR":"FMFT"
               }

rest = {"FF_DDUR":'dashed',
               "FMFF_DDUR": 'dotted',
               "FF_LIST":   'dashdot',
               "FF_DREQ":   'dashdot',
               "NF_DDUR":'--',
               "BFD_DDUR":'--',
               "FMFFTid_DDUR":"FMFT",
               "lb":"solid"
               }

m = {          "FF_DDUR":'*',
               "FMFF_DDUR": '+',
               "FF_LIST":   'x',
               "FF_DREQ":   'd',
               "NF_DDUR":'1',
               "BFD_DDUR":'2',
               "FMFFTid_DDUR":"FMFT",
               "lb":"."
               }


#['solid' | 'dashed', 'dashdot', 'dotted' | (offset, on-off-dash-seq) | '-' | '--' | '-.' | ':' | 'None' | ' ' | '' ]


if __name__ == '__main__':

    bucketSize = 2
    #instToPlot = range(1, 24) + ["_1-24"]
    #instToPlot = [1, 2, 3, 4, 5, 6, 8, 10, 12, 23] + ["_1-24"]
    instToPlot = [10]
    #instToPlot = ["_1-24"]

    hToPlot = [

    "FF_DDUR",
    "FF_DREQ",
    "FF_LIST",
    "NF_DDUR",
    #"NF_DREQ",
    #"NF_LIST",
    #"BFR_LIST",
    #"BFR_DDUR",
    #"BFR_DREQ",
    #"BFD_LIST",
    "BFD_DDUR",
    #"BFD_DREQ",
    "FMFF_DDUR",
    #"FMF_DDUR",
    #"FMFFTid_DDUR"
    ]


    #plotFreqInTimeOnHour()
    #plotFreqInTime()
    #plotNumMachine(hToPlot, bucketSize, instToPlot)
    plotAllocatedSpace(hToPlot, bucketSize, instToPlot)

    #plotCumAllocatedSpace(hToPlot, bucketSize, instToPlot)
    #plotGapToLb(hToPlot, bucketSize, instToPlot)
    #plotCumGapToLb(hToPlot, bucketSize, instToPlot)
    #plotNormGapToLb(hToPlot, bucketSize, instToPlot)



    #plotSolvingTimes(hToPlot, bucketSize, instToPlot)
    #plotBoxTimes(hToPlot, bucketSize, instToPlot)

    #plotCumSolvingTimes(hToPlot, bucketSize, instToPlot)
    #plotCumNormGapToLb(hToPlot, bucketSize, instToPlot)


    #instToPlot = range(1, 12)
    #hToPlot = [
    #"FF_DDUR",
    #"FF_LIST",
    #"NF_DDUR" ,
    #"NF_LIST" ,
    #"FMF_DDUR"
    #]

    #plotDistDurationAll(bucketSize, instToPlot)
    #plotDistReqsAll(bucketSize, instToPlot)
