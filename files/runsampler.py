from getconfigs import GetConfigs

import numpy as np
import matplotlib.pyplot as plt
import npcompare as npc
import pickle

from scipy.integrate import quad as integrate
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from matplotlib.backends.backend_pdf import PdfPages

import sys
argv = sys.argv
if len(argv) >= 3:
    if argv[1] == "type":
            mtype = argv[2]

#Here we have some code for easy loading and saving the compiled
#Stan model to a temporary dir for reuse over sections
try:
    f = open("/tmp/modelEstimateBFSmixture", "rb")
    npc.EstimateBFS._smodel_mixture = pickle.load(f)
except (IOError, EOFError):
    f = open("/tmp/modelEstimateBFSmixture", "wb")
    npc.EstimateBFS().compilestanmodel()
    pickle.dump(npc.EstimateBFS._smodel_mixture, f)
finally:
    if f:
        f.close()

#Configurations
nmaxcomp = 10
niter = 10000
try:
    mtype
except NameError:
    mtype = input("Inform mtype:\n")

if mtype != "real":
    mtype = int(mtype)

#Samples every model to list estobjlist
if mtype == "real":
    ndatasets = 3
    iterseedover = ["MCD", "CG", "AD"]
    estobjlist = dict()
    configslist = dict()
else:
    ndatasets = 100
    iterseedover = range(ndatasets)
    estobjlist = list(range(ndatasets))
    configslist = list(range(ndatasets))

for seed in iterseedover:
    filename = "results/mixture/model_seed_{}_type_{}".format(seed, mtype)
    configs = GetConfigs(mtype, seed, nmaxcomp)
    try:
        f = open(filename, "rb")
        estobj = pickle.load(f)
        print("Loaded ", filename)
    except (IOError, EOFError):
        print("Sampling ", filename)
        estobj = npc.EstimateBFS(configs.y, nmaxcomp, transformation=configs.transformation)
        estobj.sampleposterior(niter, nchains=3)
    finally:
        if f:
            f.close()

    if not len(estobj.egresults):
        print("Evaluating grid for ", filename)
        estobj.evalgrid()
        f = open(filename, "wb")
        pickle.dump(estobj, f)
        f.close()
        print("Saved ", filename)

    estobjlist[seed] = estobj
    configslist[seed] = configs

    #just to save some memory
    del(estobjlist[seed].sfit)

estobjlist

#Set limits of integration and plot limits
if mtype == 1:
    illower = -np.inf
    ilupper = np.inf
    pllower = -10
    plupper = 10
else:
    illower = 0
    ilupper = 1
    pllower = 0
    plupper = 1

if mtype != "real":
    #Get KDE estimation objects
    kde_filename = "results/kde_model_"
    kde_filename += "type_" + str(mtype)
    try:
        f = open(kde_filename, "rb")
        kdeobjlist = pickle.load(f)
        print("Loaded ", kde_filename)
    except (IOError, EOFError):
        kdeobjlist = list(range(ndatasets))
        bwobjlist = np.empty(ndatasets)
        paramsforkdecv = {'bandwidth': np.logspace(-2, 3, 100)}
        for i in range(ndatasets):
            grid = GridSearchCV(KernelDensity(), paramsforkdecv)
            grid.fit(configslist[i].y.reshape((-1,1)))
            kdeobjlist[i] = grid.best_estimator_
            bwobjlist[i] = grid.best_params_['bandwidth']
            print("Done obtaining KDE for dataset ", i)
        f = open(kde_filename, "wb")
        pickle.dump(kdeobjlist, f)
    finally:
        if f:
            f.close()

    #Get integrated errors
    interr_filename = "results/interr_model_"
    interr_filename += "type_" + str(mtype)
    try:
        f = open(interr_filename, "rb")
        errorint = pickle.load(f)
        print("Loaded ", interr_filename)
    except (IOError, EOFError):
        errorint = dict()
        for emethod in ["KDE", "BFS"]:
            errorint[emethod] = np.empty(ndatasets)
        for i in range(ndatasets):
            kdeobj = kdeobjlist[i]
            bfsobj = estobjlist[i]
            errorint["BFS"][i] = integrate(lambda x: np.square(bfsobj.evaluate(x) - configslist[i].truedensity(x)), illower, ilupper)[0]
            errorint["KDE"][i] = integrate(lambda x: np.square(np.exp(kdeobj.score(x)) - configslist[i].truedensity(x)), illower, ilupper)[0]
            print("Done evaluating integrated errors for dataset ", i)

        f = open(interr_filename, "wb")
        pickle.dump(errorint, f)
    finally:
        if f:
            f.close()

        errorintavg = dict()
        for emethod in errorint.keys():
            errorintavg[emethod] = errorint[emethod].mean()

    #Get errors over a grid of points
    errgrid_filename = "results/errgrid_model_"
    errgrid_filename += "type_" + str(mtype)
    try:
        f = open(errgrid_filename, "rb")
        (gridpoints, truedensity, errorovergrid,
         bfspredict, kdepredict) = pickle.load(f)
        print("Loaded ", errgrid_filename)
    except (IOError, EOFError):
        gridpoints = estobj.egresults["gridpoints"]
        truedensity = configs.truedensity(gridpoints)
        errorovergrid = dict()
        for emethod in ["KDE", "BFS"]:
            errorovergrid[emethod] = np.empty((gridpoints.size, ndatasets))
        for i in range(ndatasets):
            kdepredict = np.exp(kdeobjlist[i].score_samples(gridpoints.reshape(-1,1)))
            bfspredict = estobjlist[i].egresults["densitymixmean"]
            errorovergrid["BFS"][:, i] = np.square(truedensity - bfspredict)
            errorovergrid["KDE"][:, i] = np.square(truedensity - kdepredict)
        f = open(errgrid_filename, "wb")
        pickle.dump([gridpoints, truedensity, errorovergrid,
                     bfspredict, kdepredict], f)
    finally:
        if f:
            f.close()

        errorovergridavg = dict()
        for emethod in errorovergrid.keys():
            errorovergridavg[emethod] = errorovergrid[emethod].mean(1)

        p1 = plt.figure().add_subplot(111)
        p1.plot(gridpoints, bfspredict, ls="--", color="g",
                label="BFS", lw=2.2)
        p1.plot(gridpoints, kdepredict, ls=":", color="b",
                label="KDE", lw=2.5)
        p1.plot(gridpoints, truedensity, ls="-", color="r",
                label="True density")

        p1.set_xlim(pllower, plupper)
        p1.set_xlabel("y")
        p1.set_ylabel("(Estimated) density")

        legend = p1.legend(shadow=True, loc='best', frameon=True,
                           fancybox=True, borderaxespad=.5)
        frame = legend.get_frame()
        frame.set_facecolor('0.90')

        ps = PdfPages("plots/density_type_" + str(mtype) + ".pdf")
        ps.savefig(p1.get_figure(), bbox_inches='tight')
        ps.close()

        p2 = plt.figure().add_subplot(111)
        p2.plot(gridpoints, errorovergridavg["BFS"], ls="-", color="g",
                label="BFS")
        p2.plot(gridpoints, errorovergridavg["KDE"], ls=":", color="b",
                label="KDE", lw=2.5)

        p2.set_xlim(pllower, plupper)
        p2.set_xlabel("y")
        p2.set_ylabel("Estimated error")

        legend = p2.legend(shadow=True, loc='best', frameon=True,
                           fancybox=True, borderaxespad=.5)
        frame = legend.get_frame()
        frame.set_facecolor('0.90')

        ps = PdfPages("plots/errgrid_type_" + str(mtype) + ".pdf")
        ps.savefig(p2.get_figure(), bbox_inches='tight')
        ps.close()

        if mtype == 2:
            path = "results/mixture/model_seed_10_type_2"
            with open(path, 'rb') as f:
                estobj = pickle.load(f)

            pe1 = plt.subplots(2, 3, sharex=True, sharey=True)
            npe1 = np.array(pe1[1]).ravel()
            for i in range(6):
                if i == 5:
                    j = None
                    title = 'Estimated density\nfor mixture'
                else:
                    j = i*2
                    title = 'Estimated density\nfor I='+str(j+1)
                estobj.plot(ax=npe1[i], ls="-", color="g",
                            component=j, label="BFS component")
                npe1[i].plot(gridpoints, truedensity, ls=":", color="r",
                             lw=2.2, label="True density")
                npe1[i].set_title(title)
                npe1[i].set_aspect('auto')

            pe1[0].subplots_adjust(hspace=0.5)
            pe1[0].subplots_adjust(wspace=0.2)
            pe1[0].set_size_inches(6, 4)
            ps = PdfPages("plots/density_components.pdf")
            ps.savefig(pe1[0], bbox_inches='tight')
            ps.close()
#Plot real data
else:
    p = estobjlist["MCD"].plot(ls="--", color="g", label="MCD")
    estobjlist["AD"].plot(p, ls=":", color="r", label="AD")
    estobjlist["CG"].plot(p, ls="-", color="b", label="CG")
    legend = p.legend(shadow=True, frameon=True, loc='best',
                      fancybox=True, borderaxespad=.5)
    frame = legend.get_frame()
    frame.set_facecolor('0.90')

    ps = PdfPages("plots/density_type_real.pdf")
    ps.savefig(p.get_figure(), bbox_inches='tight')
    ps.close()
