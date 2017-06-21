import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pickle
import npcompare

names = list()

machine_names = np.empty(0)
dotvals = np.empty((0,2))

boxvals = list()

metricobjlist = list()

iterover = [[1, 1], [2, 2], [3, 3], [1, 2], [1, 3], [2, 3]]
for i in range(6):
    mtype1 = iterover[i][0]
    mtype2 = iterover[i][1]

    filename_dotplot = ("results/metric/dotplot_type_{}_type_{}"
                        .format(mtype1, mtype2))
    with open(filename_dotplot, "rb") as f:
        [metricobj, prob_leq_eps0] = pickle.load(f)

    names.append("{} against {}".format(mtype1, mtype2))

    machine_name = i+1
    machine_names = np.hstack((machine_names, machine_name))
    repmn = np.repeat(machine_name, prob_leq_eps0.size)
    dotval = np.column_stack((repmn, prob_leq_eps0))
    dotvals = np.vstack((dotvals, dotval))

    boxvals.append(prob_leq_eps0)

    metricobjlist.append(metricobj)


#Dot plot
dotplot = plt.scatter(dotvals[:, 0], dotvals[:, 1], marker='o', s=15.0,
                      color="green").get_figure()
dotplot.set_size_inches(7.3, 5)

ax1 = dotplot.get_axes()[0]
ax1.set_xlabel("Models compared")
ax1.set_ylabel("Probability")
#ax1.set_ylim(0.9, 1.05)


#Box plot
bplot = ax1.boxplot(boxvals, whis='range', showmeans=True,
                    meanline=True)

for mean in bplot['means']:
    mean.set(color='#FF6600')

for median in bplot['medians']:
    median.set(color='blue')

ax1.set_xlabel("Models compared")
ax1.set_ylabel("Probability")
ax1.set_xticklabels(names)

ps = PdfPages("plots/dotplot.pdf")
ps.savefig(dotplot, bbox_inches='tight')
ps.close()


#Single dataset plot
cls = [":", "-", "-.", "--", "-", "-."]
clw = [2.2, 2.2, 2.2, 2.2, 1.0, 1.0]
ax2 = None
for i in range(6):
    ax2 = metricobjlist[i].plot(ax=ax2, label=names[i],
                                linestyle=cls[i], lw=clw[i])

legend = ax2.legend(shadow=True, frameon=True, loc='best',
                    fancybox=True, borderaxespad=.5)

ax2.set_xlabel(r'$\epsilon$')
ax2.set_ylabel("Probability")

ps = PdfPages("plots/metric_single_all.pdf")
ps.savefig(ax2.get_figure(), bbox_inches='tight')
ps.close()
