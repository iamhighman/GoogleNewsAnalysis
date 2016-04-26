# map_us.R - a set of utility functions
# Yu-Ru Lin
# date: June 12, 2012
# usage: 
#   source('../../Rs/map_us.R')

source('../../Rs/utils.R')

read.state.abbs2name <- function() {
  ## url <- 'http://www.census.gov/popest/geographic/state_geocodes_v2009.txt'
  ifilename <- '../data/state_fips.txt'
  X <- read.csv(file=ifilename,head=F,skip=1,sep="\t",strip.white =T,stringsAsFactors=F)
  stateabbs2name <- list()
  for (i in 1:nrow(X)) {
    stateabbs2name[[X$V1[i]]] <- tolower(X$V3[i])
  }
  stateabbs2name  
}

get_lm_res <- function(vars,X) {
  y <- vars[1]
  vars <- vars[-1]
  vstr <- paste(vars,sep='',collapse='+')
  modelname <- paste(y,vstr,sep='~')
  cat('pred:',modelname,'\n')
  f <- as.formula(modelname)
  pred <- lm(f,weights=X$w,data=X);debug(summary(pred))  
  resid(pred)
}

get_picked_vars <- function(X,pick) {
  #pick1=var1; pick2=var2; pick3=var3; pick4=state
  var <- colnames(X)[1]
  pvar <- c(var,var,var,NA)
  for (j in 1:2) {
    if (pick[j]!='.') pvar[j] <- pick[j]
  }
  if (pick[3]!='.' && pick[3]!='res') pvar[3] <- pick[3]
  
  X$v1 <- X[,pvar[1]] #predictor    
  X$v2 <- X[,pvar[2]] #predictor    
  X$v3 <- X[,pvar[3]] #predictor    
  picked <- list(X=X,pvar=pvar)
  picked
}
get_picked_states <- function(X,pick) {
  all_states <- map_data("state")
  state.info = data.frame(state.center, state.abb);
  state.info = subset(state.info, !state.abb %in% c("AK", "HI"));
  in.state <- pick[4]
  if (in.state=='.') {
    states <- all_states
#     opts$in.state <- ''
  }
  else {
    stateabbs2name <- read.state.abbs2name()
    statename <- stateabbs2name[[in.state]][[1]]
    states <- subset(all_states, region %in% c(statename))
    state.info = subset(state.info, state.abb %in% c(in.state));
#     opts$in.state <- in.state
    X$statename <- as.character(X$statename)
    X <- subset(X, statename==in.state)
  }
  latrange <- range(states$lat)
  lonrange <- range(states$long)  
  picked <- list(X=X,states=states,state.info=state.info,latrange=latrange,lonrange=lonrange,in.state=in.state)
}
plot_map <- function(popts) {
  rplot_init()
  lib_init(c('maps','RColorBrewer'))
  theme_update(panel.background=theme_blank(), 
               panel.grid.major=theme_blank(),
               panel.grid.minor=theme_blank(),
               panel.border=theme_blank())
  
  opts<-popts$opts; pick<-popts$pick; plotname<-popts$plotname; 
  X <- popts$X; vars <- popts$vars
#   popts$alpha=0.5;popts$size=10;popts$arrowlen=0.3
  
  picked <- get_picked_vars(X,pick)
  X<-picked$X; pvar<-picked$pvar
  
  picked <- get_picked_states(X,pick)
  X<-picked$X; states<-picked$states; state.info<-picked$state.info; latrange<-picked$latrange; lonrange<-picked$lonrange; in.state<-picked$in.state;
  
  # exclude the 3rd in LM model
  if (pick[3]!='.') {
    vars <- setdiff(vars,pvar[3])
    X$w <- NULL
    X$res <- get_lm_res(vars,X)
    if (pick[3]!='res') {
      vars <- c('res',var3)
      X$res <- X$res-get_lm_res(vars,X)
    }
    X$r <- abs(X$res)*popts$arrowlen
#     X$r <- abs(X$res / max(abs(X$res))) #abs(scale(X$res,center=T,scale=T))/4
    X$theta <- (X$res / max(abs(X$res)))
    X$theta <- X$theta*pi/2
    X$xend <- X$lon+X$r*cos(X$theta)
    X$yend <- X$lat+X$r*sin(X$theta)      
    
    lonrange <- range(states$lon)
    latrange <- range(c(states$lat,X$yend))
  }
  
  p <- ggplot()
  # plot map polygon shapes (state boundaries)
  p <- p + geom_polygon( data=states, aes(x=long, y=lat, group = group),colour="gray80", fill="white" )
  # var1 as size, var2 as color
  if (pick[2]!='.') {
    p <- p + geom_point( data=X, aes(x=lon, y=lat, size=v1,colour=v2), alpha=popts$alpha) + 
      scale_size(name=pvar[1],to=c(1,popts$size))+
      scale_colour_gradient(limits=range(X$v2), low="yellow", high="red", space="Lab",name=pvar[2])    
  }
  p <- p + scale_x_continuous(limits = lonrange)
  p <- p + scale_y_continuous(limits = latrange)
  if (popts$showlabel) {
    # show state name
    p <- p+ geom_text(data = state.info, aes(x = x, y = y, label = state.abb),
                      colour = 'gray70')
    # show county name
    if (in.state!='.') p <- p+ geom_text(data = X, aes(x = lon, y = lat, label = cntyname),size=5,
                                         colour = 'gray10')
  }
  
  if (pick[3]!='.') {
    # draw arrow head if in a state
    if (in.state!='.') p <- p + geom_segment(data=X, aes(x=lon,y=lat,xend=xend,yend=yend),width=0.1,alpha=0.6,size=0.3,
                                             arrow=arrow(length=unit(0.1,"cm"))) 
    else p <- p + geom_segment(data=X, aes(x=lon,y=lat,xend=xend,yend=yend),width=0.1,alpha=0.6,size=0.3,
    ) 
  }
  
  print(p)
}

filter_X <- function(X,upper,lower) {
  breaks <- quantile(X$v1,probs=c(lower/100,upper/100))
  lower_val <- breaks[1]
  upper_val <- breaks[2]
  X <- subset(X,v1>=lower_val & v1<=upper_val)
  X
}

plot_scatterplot <- function(popts) {
  rplot_init()
  lib_init(c('maps','RColorBrewer'))
  opts<-popts$opts; pick<-popts$pick; plotname<-popts$plotname; 
  X <- popts$X; vars <- popts$vars
  #   popts$alpha=0.5;popts$size=10;popts$arrowlen=0.3
  
  picked <- get_picked_vars(X,pick)
  X<-picked$X; pvar<-picked$pvar
  
  picked <- get_picked_states(X,pick)
  X<-picked$X; states<-picked$states; latrange<-picked$latrange; lonrange<-picked$lonrange; in.state<-picked$in.state;
  
  if (pick[3]!='.') {
    vars <- setdiff(vars,pvar[3])
    X$w <- NULL
    X$res <- get_lm_res(vars,X)
    X$v2 <- X$res
    pvar[2] <- paste(pvar[3],'res',sep='_')
  }
  
  xrange <- range(X$v1)
  yrange <- range(X$v2)
  Y <- filter_X(X,popts$upper,popts$lower)
  
  p <- ggplot()
  p <- p + geom_point( data=X, aes(x=v1, y=v2), size=.5*popts$size, colour='gray10', alpha=popts$alpha)
#   p <- p + geom_point( data=X, aes(x=v1, y=v2, size=v1,colour=v2), alpha=popts$alpha) +
#     scale_size(name=pvar[1],to=c(1,popts$size))+
#     scale_colour_gradient(limits=range(X$v2), low="yellow", high="red", space="Lab",name=pvar[2])    
  p <- p + scale_x_continuous(limits = xrange,name=pvar[1])
  p <- p + scale_y_continuous(limits = yrange,name=pvar[2])
  
  if (popts$showlabel) {
    Y$name <- paste(Y$cntyname,Y$statename,sep=',')
    # show county+state name
    p <- p+ geom_text(data = Y, aes(x = v1, y = v2, label = name),size=4,
                                         colour = 'gray10')
  }
  
  print(p)
}
