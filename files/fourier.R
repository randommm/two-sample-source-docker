pdf("plots/fourier.pdf")
x <- seq(from=0,to=1,by=0.001)
plot(x, sqrt(2)*cos(2*pi*x), col=2, type="l",
     ylim=c(-sqrt(2)-.1, sqrt(2)+.2), xlab="x",
     ylab=expression(phi[i]), cex.lab=1.5)
lines(x,sqrt(2)*cos(4*pi*x),col=3,type="l")
lines(x,sqrt(2)*cos(6*pi*x),col=4,type="l")
abline(h=1,col=1)
legend("top", ,c(expression(phi[0]), expression(phi[2]),
       expression(phi[4]), expression(phi[6])), col=1:4, lty=1,
       horiz=TRUE, bty="n",adj=2.7, x.intersp=3)
dev.off()
