from getconfigs import GetConfigs

import numpy as np
import matplotlib.pyplot as plt
import npcompare as npc
import pickle

from scipy.integrate import quad
import scipy.stats as stats
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
from matplotlib.backends.backend_pdf import PdfPages

import sys
argv = sys.argv
if len(argv) >= 4:
    if argv[1] == "type":
        mtype1 = argv[2]
        mtype2 = argv[3]

#Configurations
nmaxcomp = 10
niter = 10000

try:
    mtype1
except NameError:
    mtype1 = input("Inform mtype1:\n")
try:
    mtype2
except NameError:
    mtype2 = input("Inform mtype2:\n")

if mtype1 != "real":
    mtype1 = int(mtype1)
if mtype2 != "real":
    mtype2 = int(mtype2)

#Samples every model to list estobjlist
if mtype1 == "real":
    ndatasets = 3
    iterseedover = [["MCD", "CG"], ["MCD", "AD"], ["CG", "AD"]]
    metricobjlist = dict()
    configslist = dict()
else:
    if mtype1 == mtype2:
        ndatasets = 50
        offset = 50
    else:
        ndatasets = 100
        offset = 0
    iterseedover = range(ndatasets)
    metricobjlist = list(range(ndatasets))
    configslist1 = list(range(ndatasets))
    configslist2 = list(range(ndatasets))
    prob_leq_eps0 = np.empty(ndatasets)

epsilon_0 = quad(lambda x: (stats.norm.pdf(x, 0)
    - stats.norm.pdf(x, 1))**2, -np.inf, np.inf)[0]
f = None

for seed in iterseedover:
    if mtype1 == "real":
        seed1 = seed[0]
        seed2 = seed[1]
    else:
        seed1 = seed
        seed2 = seed + offset
    try:
        filename = "results/metric/model_seed_{}_type_{}_against_seed_{}_type_{}".format(seed1, mtype1, seed2, mtype2)
        f = open(filename, "rb")
        metricobj = pickle.load(f)
        if not metricobj.msamples.shape[0]:
           f.close()
           raise IOError()
        print("Loaded ", filename)
    except (IOError, EOFError):
        filename1 = "results/mixture/model_seed_{}_type_{}".format(seed1, mtype1)
        filename2 = "results/mixture/model_seed_{}_type_{}".format(seed2, mtype2)
        try:
            f1 = open(filename1, "rb")
            estobj1 = pickle.load(f1)
            print("Loaded ", filename1)

            f2 = open(filename2, "rb")
            estobj2 = pickle.load(f2)
            print("Loaded ", filename2)
        except Exception:
            raise("Unable to load MCMC samples")
        finally:
            if f1:
                f1.close()
            if f2:
                f2.close()

        if mtype1 == 1 and mtype2 != 1:
            transformation = False
        else:
            transformation = True
        metricobj = npc.Compare.frombfs(estobj1, estobj2,
                                        transformation=transformation)
        metricobj.sampleposterior(10000)
    finally:
        if f:
            f.close()

        #metricobj.sampleposterior(1e4)
        f = open(filename, "wb")
        pickle.dump(metricobj, f)
        f.close()


    configs1 = GetConfigs(mtype1, seed1, nmaxcomp)
    configs2 = GetConfigs(mtype2, seed2, nmaxcomp)
    if mtype1 == "real":
        metricobjlist[seed1 + "_" + seed2] = metricobj
        configslist[seed1] = configs1
        configslist[seed2] = configs2
    else:
        metricobjlist[seed1] = metricobj
        configslist1[seed1] = configs1
        configslist2[seed1] = configs2
        prob_leq_eps0[seed1] = ((metricobj.msamples <= epsilon_0).sum()
                               / len(metricobj))


if mtype1 == "real":
    p = metricobjlist["MCD_CG"].plot(linestyle="--", color="g",
                                     label="MCD against CG")
    metricobjlist["MCD_AD"].plot(p, linestyle=":", color="r",
                                 label="MCD against AD")
    metricobjlist["CG_AD"].plot(p, linestyle="-", color="b",
                                label="CG against AD")

    p.set_xlabel(r'$\epsilon$')
    p.set_ylabel("Probability")

    legend = p.legend(shadow=True, loc='best', frameon=True,
                      fancybox=True, borderaxespad=.5)
    frame = legend.get_frame()
    frame.set_facecolor('0.90')

    ps = PdfPages("plots/metric_type_real.pdf")
    ps.savefig(p.get_figure(), bbox_inches='tight')
    ps.close()
else:
    p1 = metricobjlist[0].plot(color="blue")

    p1.set_xlabel(r'$\epsilon$')
    p1.set_ylabel("Probability")

    ps = PdfPages("plots/metric_single_type_{}_{}.pdf"
                  .format(mtype1, mtype2))
    ps.savefig(p1.get_figure(), bbox_inches='tight')
    ps.close()

    prob_leq_eps0 = np.sort(prob_leq_eps0)
    p2 = plt.figure().add_subplot(111)
    p2.plot(range(ndatasets), prob_leq_eps0, 'ro', color="blue",
            lw=0.2)
    p2.axhline(prob_leq_eps0.mean(), color="green")

    p2.set_xlabel("Dataset index")
    p2.set_ylabel("Probability")
    p2.set_ylim(0, 1)
    p2.get_figure().set_size_inches(6, 3)

    ps = PdfPages("plots/metric_leq_eps0_type_{}_{}.pdf"
                  .format(mtype1, mtype2))
    ps.savefig(p2.get_figure(), bbox_inches='tight')
    ps.close()

    filename_dotplot = ("results/metric/dotplot_type_{}_type_{}"
                        .format(mtype1, mtype2))
    with open(filename_dotplot, "wb") as f:
        pickle.dump([metricobjlist[0], prob_leq_eps0], f)
