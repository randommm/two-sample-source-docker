import numpy as np
import scipy.stats as stats
import pandas as pd
import rpy2.robjects as ro
import npcompare as npc

class GetConfigs:
    def __init__(self, mtype, seed, nmaxcomp):
        if mtype == 1:
            ro.reval("""
            set.seed({})
            y <- rnorm(50, sample(c(-2, 0, 1, 2), 50,
                       TRUE, c(.3, .2, .2, .3)))
            """.format(seed + 1))
            self.y = np.array(ro.r['y'], dtype=np.float64)
            self.transformation = "logit"
            def truedensity(y_):
                #y_unc = scipy.special.logit(y_)
                dnorm = stats.norm.pdf
                results = .3 * dnorm(y_, -2) + .2 * dnorm(y_, 0) +\
                          .2 * dnorm(y_, 1) + .3 * dnorm(y_, 2)
                return results
                #abs jacobian transform
                #return results / abs(y_ - y_**2)
            self.truedensity = truedensity
        elif mtype == 2:
            ro.reval("""
            set.seed({})
            Ns <- as.vector(rmultinom(1, 50, c(.2, .25, .35, .2)))
            y <- c(rbeta(Ns[1], 1.3, 1.3),
                   rbeta(Ns[2], 1.1, 3),
                   rbeta(Ns[3], 5, 1),
                   rbeta(Ns[4], 1.5, 4))
            """.format(seed + 1))
            self.y = np.array(ro.r['y'], dtype=np.float64)
            self.transformation = None
            def truedensity(y_):
                dbeta = stats.beta.pdf
                return (.20 * dbeta(y_, 1.3, 1.3) +
                        .25 * dbeta(y_, 1.1, 3) +
                        .35 * dbeta(y_, 5, 1) +
                        .20 * dbeta(y_, 1.5, 4))
            self.truedensity = truedensity
        elif mtype == 3:
            ro.reval("""
            set.seed({})
            y <- rbeta(50, 2, 5)
            """.format(seed + 1))
            self.y = np.array(ro.r['y'], dtype=np.float64)
            self.transformation = None
            def truedensity(y_):
                return stats.beta.pdf(y_, 2, 5)
            self.truedensity = truedensity
        elif mtype == "real":
            tab = pd.read_csv("data.csv")
            tab.dropna(inplace=True)
            self.y = tab.loc[tab.iloc[:, 0] == seed].iloc[:, 1]
            self.y = np.array(self.y, dtype=np.float64)
            self.n = self.y.size
            self.transformation = {"transf": "fixed", "vmin": 50,
                                   "vmax": 107}

        self.phi = npc.fourierseries(self.y, nmaxcomp)
