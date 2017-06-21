import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import scipy.stats as stats
from scipy.special import logit

pdf = stats.norm.pdf
gridsize = 1000
grid = logit(np.linspace(0, 1, gridsize))
pdf0 = pdf(grid, 0, 1)
pdf1 = pdf(grid, 1, 1)

ax = plt.subplot(111)
ax.plot(grid, pdf0, label=r'$\varphi_0$', ls="-", color="green")
ax.plot(grid, pdf1, label=r'$\varphi_1$', ls=":", color="blue")

legend = ax.legend(shadow=True, frameon=True, loc='best',
                   fancybox=True, borderaxespad=.5)

ps = PdfPages("plots/gaussian_densities.pdf")
ps.savefig(ax.get_figure(), bbox_inches='tight')
ps.close()
