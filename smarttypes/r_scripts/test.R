
##import diffusionMap 
library("diffusionMap")

## example with noisy spiral
# n=2000
# t=runif(n)^.7*10
# al=.15;bet=.5;
# x1=bet*exp(al*t)*cos(t)+rnorm(n,0,.1)
# y1=bet*exp(al*t)*sin(t)+rnorm(n,0,.1)
# plot(x1,y1,pch=20,main="Noisy spiral")
# D = dist(cbind(x1,y1))
# dmap = diffuse(D,neigen=2) # compute diffusion map
# plot.dmap(dmap)

# par(mfrow=c(2,1))
# plot(t,dmap$X[,1],pch=20,axes=FALSE,xlab="spiral parameter",ylab="1st diffusion coefficient")
# box()
# plot(1:10,dmap$eigenmult,type="h",xlab="diffusion map dimension",ylab="eigen-multipliers")

# ## example with annulus data set
# data(annulus)
# plot(annulus,main="Annulus Data",pch=20,cex=.7)
# D = dist(annulus) # use Euclidean distance
# dmap = diffuse(D, neigen=2)#eps.val=.1) # compute diffusion map & plot
# print(dmap)
# plot(dmap)


## example with Chainlink data set
data(Chainlink)
lab.col = c(rep("red",500),rep("blue",500)); n=1000
scatterplot3d(Chainlink$C1,Chainlink$C2,Chainlink$C3,color=lab.col,main="Chainlink Data") # plot Chainlink data
D = dist(Chainlink) # use Euclidean distance
dmap = diffuse(D,neigen=3,,eps.val=.01) # compute diffusion map & plot
plot(dmap)
print(dmap)
dkmeans = diffusionKmeans(dmap, K=2)
col.dkmeans=ifelse(dkmeans$part==1,"red","blue")
scatterplot3d(Chainlink,color=col.dkmeans,main="Chainlink Data, colored by diff. K-means class")
table(dkmeans$part,lab.col)


