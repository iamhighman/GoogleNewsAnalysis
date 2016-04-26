# utils.R - a set of utility functions
# @author: Yu-Ru Lin
# @date: June 3, 2012
# usage: 
#   source('../../myfuncs/utils.R')

debug.flag <- F

# set a prior desired mirror to avoid evoking Tcl/Tk interface
options(repos='http://r.iq.harvard.edu') # USA

# initialize libraries without printing verbose info
# usage: 
#   lib_init(c('MASS','ggplot2'))
#   ggplot_init()
lib_init <- function(liblist=c()) {
  # check required libraries; install non-installed libraries for the first time
  for (lib in liblist) {
    debug(printf('checking package %s\n',lib),flag=debug.flag)
    if (!is.installed(lib)) {
      cat('installing package',lib,'\n')
      res <- try(install.packages(lib))
      if (inherits(res, "try-error")) q(status=1) else q()
    }
    suppressPackageStartupMessages( require(lib,quietly=T,character.only=T) )
  }
}

is.installed <- function(mypkg) is.element(mypkg, installed.packages()[,1]) 

printf <- function(...) cat(sprintf(...))
pause <- function(s=NULL) {
  if (!is.null(s)) cat(s,'\n')
  readline(prompt = "Pause. Press <Enter> to continue...")
}
debug <- function(msg,flag=T,do.pause=F){
  if (flag) {
    if (typeof(msg)=='character') print(msg)
    else msg
  }
  if (do.pause) pause()
}

### string operations ###
# test if a string S contains s
has.str <- function(S,s) grepl(s,S) 

# replace the substring of str
# usage:
#   replace.str('Now is the time      ','is','was')
replace.str <- function(str,pattern,replacement) {
  # http://astrostatistics.psu.edu/su07/R/html/base/html/grep.html
  # ## trim trailing white space
  # str = 'Now is the time      '
  # sub(' +$', '', str)  ## spaces only
  # sub('[[:space:]]+$', '', str) ## white space, POSIX-style
  # sub('\\s+$', '', str, perl = TRUE) ## Perl-style white space
  gsub(pattern, replacement, str) 
}

# return the matched indices of x and y
# usage:
#   x= 2:10; y= c(1,3,5,9); m <- match.idx( x, y )
#   print(m$idx); print(m$ix); print(m$iy)
#   print(x[m$ix]); print(y[m$iy]) # the intersection values
match.idx <- function(x,y) {
  idx <- match(x,y)
  iy <- na.omit(idx); ix <- which(idx>0)
  list(idx=idx,ix=ix,iy=iy)
}
### date/time operations ###
daynum2datestr <- function(ti,start='2011-01-01',oformat='%Y%m%d') {
  strftime(strptime(start,'%Y-%m-%d')+ 86400*(ti-1),oformat)
}
datestr2daynum <- function(ts,iformat='%Y%m%d') {
  as.numeric(strftime(strptime(ts,iformat),'%j'))
}

# rename the columen names in a dataframe; 
# avoiding the use of 'reshape' package (not available at earlier R version)
# usage:
#   X <- rename(X,c(population='pop',income='inc')
rename <- function(x, replace) {
  replacement <-  replace[names(x)]
  names(x)[!is.na(replacement)] <- replacement[!is.na(replacement)]
  x
}

### file I/O ###
save.RData <- function(X,ofilename) {
  save(X,file=ofilename)
  cat('save to ',ofilename,'\n')
}
load.RData <- function(ofilename,na.action.='omit') {
  if (file.exists(ofilename)) {
    cat('loading ',ofilename,'\n')
    load(ofilename)
    return(X)
  }
  if (na.action.=='stop') stop(sprintf('file not found: %s',ofilename))
  else sprintf('file not found: %s',ofilename)
  NULL
}

# return a dictionary (hash object) with the i-th column as keys and 1:nrow(X) as values
# usage:
#   a2i <- load.dict('test/les2num.txt'); print(keys(a2i)); print(values(a2i))
#   print( a2i[['Wyden:D:OR:Sen']] )
#   print( has.key('Webb:D:VA:Sen',a2i) )
load.dict <- function(ifilename,header=F,sep=',',icol=1) {
  suppressPackageStartupMessages( require(hash) )  
  X <- read.csv(ifilename,header=header,sep=sep,stringsAsFactors=F)
  printf('load %d rows,%s cols from %s\n',nrow(X),ncol(X),ifilename)  
  x <- hash(keys=X[,icol],values=1:nrow(X))
  x
}
# reverse the dictionary
reverse.dict <- function(a2i) {
  suppressPackageStartupMessages( require(hash) )  
  i2a <- hash(keys=values(a2i),values=keys(a2i))
  i2a
}
# return the i-th column as a list
load.list <- function(ifilename,header=F,sep=',',icol=1) {
  X <- read.csv(ifilename,header=header,sep=sep,stringsAsFactors=F)
  printf('load %d rows,%s cols from %s\n',nrow(X),ncol(X),ifilename)  
  X[,icol]
}
# save image to various formats
save.img <- function(filename,fileformat='pdf',ofilepath.=ofilepath) {
  ofilename <- sprintf('%s/%s.%s',ofilepath.,filename,fileformat)
  if (fileformat=='pdf') dev.print(device=pdf, ofilename)
  if (fileformat=='png') png(ofilename)
  if (fileformat=='jpg') jpeg(ofilename)
  if (fileformat=='eps') dev.print(device=eps, ofilename)
  printf('save img to %s\n',ofilename)
}

### (sparse) matrix operations ###
# load the edgelist file (source_id,target_id,edge_weight) into a sparseMatrix
load.matrix <- function(ifilename,Ns=NULL,offset=0,weighted=T) {
  require(Matrix);require(MASS)
  if (weighted) {
    x <- scan(ifilename,what=list(integer(),integer(),numeric()),sep='\t')
    if (is.null(Ns)) {
      #N = max( max(x[[1]])+offset, max(x[[2]])+offset )
      ni = max(x[[1]])+offset 
      nj = max(x[[2]])+offset 
      M <- sparseMatrix(i=x[[1]]+offset,j=x[[2]]+offset,x=x[[3]],dims=c(ni,nj))      
    }
    else M <- sparseMatrix(i=x[[1]]+offset,j=x[[2]]+offset,x=x[[3]],dims=Ns)
  } else {
    x <- scan(ifilename,what=list(integer(),integer()))
    if (is.null(Ns)) {
      #N = max( max(x[[1]])+offset, max(x[[2]])+offset )
      ni = max(x[[1]])+offset 
      nj = max(x[[2]])+offset 
      M <- sparseMatrix(i=x[[1]]+offset,j=x[[2]]+offset,x=rep(1,length(x[[1]])),dims=c(ni,nj))      
    }
    else M <- sparseMatrix(i=x[[1]]+offset,j=x[[2]]+offset,x=rep(1,length(x[[1]])),dims=Ns)
  }
  cat('load from ',ifilename,'\n',dim(M),',',object.size(M),',',nnzero(M),'\n')
  M
}

# load the market matrix format
load.mtx <- function(ifilename) {
  M <- readMM(ifilename)
  cat('load from ',ifilename,'\n',dim(M),',',object.size(M),',',nnzero(M),class(M),'\n')
  M
}

### safe operations ###
safe.divide <- function(x,y,NAvalue=0) {
  sapply(1:length(x),
         function(i,x,y) {
           a=x[i];b=y[i];
           if (is.na(a) || is.na(b) || b<=0) NAvalue else a/b},
         x,y)
}
safe.colMeans <- function(v) {
  if (length(dim(v))==2) colMeans(v)
  else if (length(v)>0) {cat('single vector dim=',length(v),'.\n'); v}
  else NULL
}
safe.rowMeans <- function(v) {
  if (length(dim(v))==2) rowMeans(v)
  else if (length(v)>0) {cat('single vector dim=',length(v),'.\n'); v}
  else NULL
}
# compute the column variations for the input matrix x
# usage:
#   x <- cbind(x1 = 3, x2 = c(4:1, 2:5))
#   rowSums(x); colSums(x)
#   rowMeans(x); colMeans(x)
#   rowVars(x); colVars(x)
colVars <- function(x, na.rm=FALSE, dims=1, unbiased=TRUE, SumSquares=FALSE,
                    twopass=FALSE) {
  if (SumSquares) return(colSums(x^2, na.rm, dims))
  N <- colSums(!is.na(x), FALSE, dims)
  Nm1 <- if (unbiased) N-1 else N
  if (twopass) {x <- if (dims==length(dim(x))) x - mean(x, na.rm=na.rm) else
    sweep(x, (dims+1):length(dim(x)), colMeans(x,na.rm,dims))}
  (colSums(x^2, na.rm, dims) - colSums(x, na.rm, dims)^2/N) / Nm1
}
# compute the row variations for the input matrix x
rowVars <- function(x, na.rm=FALSE, dims=1, unbiased=TRUE, SumSquares=FALSE,
                    twopass=FALSE) {
  return(colVars(t(x),na.rm,dims,unbiased,SumSquares,twopass))
}
# return the median (or percentile) index
# usage:
#   x <- c(1:4,0:5,11)
#   which.min(x); which.max(x); which.median(x)
which.median <- function(x,q=0.5) {
  breaks <- quantile(x,probs=c(q,1))
  debug(print(breaks),flag=debug.flag)
  ii <- which(x >= breaks[1] & x <=breaks[2])
  s <- sort(x[ii],index.return=T)
  i <- ii[s$ix[1]]
  #   names(i) <- names(x)[i]
  i
}


### statistic summary ###
# print correlation of two vector x and y, with significance indicating by star
# usage: 
#   x1 = c(5:20, 1:40); x2 = c(5:10, 1:50)
#   corstar(x1,x2)
corstar <- function(x,y,digits=2,type='pearson') {
  suppressPackageStartupMessages( require(Hmisc) )
  mystars <- function(p) {ifelse(p < .001, "***", ifelse(p < .05, "*", ""))}
  r <- abs(cor(x, y))
  xy <- as.matrix(cbind(x,y))
  r <- rcorr(xy,type=type)$r
  p <- rcorr(xy,type=type)$P; #print(p)
  r <- round(r[1,2],2)
  txt <- sprintf('%s%s',r,mystars(p[1,2]))
  txt
}
# print correlation matrix, with significance indicating by stars
# usage:
#   x <- cbind(x1 = c(5:2, 1:4), x2 = c(4:1, 2:5))
#   corstars(x)
corstars <- function(mX,sep.='|',type='pearson',digit=3){
  # mX is data frame with relevant columns, e.g.
  # mX <- X[vars]
  suppressPackageStartupMessages( require(Hmisc) )
  
  x <- as.matrix(mX)
  R <- rcorr(x,type=type)$r
  p <- rcorr(x,type=type)$P
#   mystars <- ifelse(p < .01, "**|", ifelse(p < .05, "* |", "  |"))
#   mystars <- ifelse(p < .01, sprintf("**%s",sep.), ifelse(p < .05, sprintf("* %s",sep.), sprintf("  %s",sep.)))
  mystars <- ifelse(p<.001, sprintf("***%s",sep.), ifelse(p < .01, sprintf("**%s",sep.), ifelse(p < .05, sprintf("* %s",sep.), sprintf("  %s",sep.))))
  R <- format(round(cbind(rep(-1.111, ncol(x)), R), digit))[,-1]
  Rnew <- matrix(paste(R, mystars, sep=""), ncol=ncol(x))
#   diag(Rnew) <- paste(diag(R), "  |", sep="")
  diag(Rnew) <- paste(diag(R), sprintf("  %s",sep.), sep="")
  rownames(Rnew) <- colnames(x)
#   colnames(Rnew) <- paste(colnames(x), "  |", sep="")
  colnames(Rnew) <- paste(colnames(x), sprintf("  %s",sep.), sep="")
  Rnew <- as.data.frame(Rnew)
  return(Rnew)
}

# The following functions summarySE, normDataWithin, summarySEwithin were written by Winston Chang (winston@stdout.org). 
# @see http://wiki.stdout.org/rcookbook/Graphs/Plotting%20means%20and%20error%20bars%20(ggplot2)/
## Summarizes data.
## Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
##   data: a data frame.
##   measurevar: the name of a column that contains the variable to be summariezed
##   groupvars: a vector containing names of columns that contain grouping variables
##   na.rm: a boolean that indicates whether to ignore NA's
##   conf.interval: the percent range of the confidence interval (default is 95%)
summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE,
                      conf.interval=.95, .drop=TRUE) {
  suppressPackageStartupMessages( require(plyr) )
  
  # New version of length which can handle NA's: if na.rm==T, don't count them
  length2 <- function (x, na.rm=FALSE) {
    if (na.rm) sum(!is.na(x))
    else       length(x)
  }
  
  # This is does the summary; it's not easy to understand...
  datac <- ddply(data, groupvars, .drop=.drop,
                 .fun= function(xx, col, na.rm) {
                   c( N    = length2(xx[,col], na.rm=na.rm),
                      mean = mean   (xx[,col], na.rm=na.rm),
                      sd   = sd     (xx[,col], na.rm=na.rm)
                   )
                 },
                 measurevar,
                 na.rm
  )
  
  # Rename the "mean" column    
  datac <- rename(datac, c("mean"=measurevar))
  
  datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean
  
  # Confidence interval multiplier for standard error
  # Calculate t-statistic for confidence interval: 
  # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
  ciMult <- qt(conf.interval/2 + .5, datac$N-1)
  datac$ci <- datac$se * ciMult
  
  return(datac)
}

## Norms the data within specified groups in a data frame; it normalizes each
## subject (identified by idvar) so that they have the same mean, within each group
## specified by betweenvars.
##   data: a data frame.
##   idvar: the name of a column that identifies each subject (or matched subjects)
##   measurevar: the name of a column that contains the variable to be summariezed
##   betweenvars: a vector containing names of columns that are between-subjects variables
##   na.rm: a boolean that indicates whether to ignore NA's
normDataWithin <- function(data=NULL, idvar, measurevar, betweenvars=NULL,
                           na.rm=FALSE, .drop=TRUE) {
  suppressPackageStartupMessages( require(plyr) )
  
  # Measure var on left, idvar + between vars on right of formula.
  data.subjMean <- ddply(data, c(idvar, betweenvars), .drop=.drop,
                         .fun = function(xx, col, na.rm) {
                           c(subjMean = mean(xx[,col], na.rm=na.rm))
                         },
                         measurevar,
                         na.rm
  )
  
  # Put the subject means with original data
  data <- merge(data, data.subjMean)
  
  # Get the normalized data in a new column
  measureNormedVar <- paste(measurevar, "Normed", sep="")
  data[,measureNormedVar] <- data[,measurevar] - data[,"subjMean"] +
    mean(data[,measurevar], na.rm=na.rm)
  
  # Remove this subject mean column
  data$subjMean <- NULL
  
  return(data)
}

## Summarizes data, handling within-subjects variables by removing inter-subject variability.
## It will still work if there are no within-S variables.
## Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
## If there are within-subject variables, calculate adjusted values using method from Morey (2008).
##   data: a data frame.
##   measurevar: the name of a column that contains the variable to be summariezed
##   betweenvars: a vector containing names of columns that are between-subjects variables
##   withinvars: a vector containing names of columns that are within-subjects variables
##   idvar: the name of a column that identifies each subject (or matched subjects)
##   na.rm: a boolean that indicates whether to ignore NA's
##   conf.interval: the percent range of the confidence interval (default is 95%)
summarySEwithin <- function(data=NULL, measurevar, betweenvars=NULL, withinvars=NULL,
                            idvar=NULL, na.rm=FALSE, conf.interval=.95, .drop=TRUE) {
  
  # Ensure that the betweenvars and withinvars are factors
  factorvars <- sapply(data[, c(betweenvars, withinvars), drop=FALSE], FUN=is.factor)
  if (!all(factorvars)) {
    nonfactorvars <- names(factorvars)[!factorvars]
    message("Automatically converting the following non-factors to factors: ",
            paste(nonfactorvars, collapse = ", "))
    data[nonfactorvars] <- lapply(data[nonfactorvars], factor)
  }
  
  # Norm each subject's data    
  data <- normDataWithin(data, idvar, measurevar, betweenvars, na.rm, .drop=.drop)
  
  # This is the name of the new column
  measureNormedVar <- paste(measurevar, "Normed", sep="")
  
  # Replace the original data column with the normed one
  data[,measurevar] <- data[,measureNormedVar]
  
  # Collapse the normed data - now we can treat between and within vars the same
  datac <- summarySE(data, measurevar, groupvars=c(betweenvars, withinvars), na.rm=na.rm,
                     conf.interval=conf.interval, .drop=.drop)
  
  # Apply correction from Morey (2008) to the standard error and confidence interval
  #  Get the product of the number of conditions of within-S variables
  nWithinGroups    <- prod(sapply(datac[,withinvars, drop=FALSE], FUN=nlevels))
  correctionFactor <- sqrt( nWithinGroups / (nWithinGroups-1) )
  
  # Apply the correction factor
  datac$sd <- datac$sd * correctionFactor
  datac$se <- datac$se * correctionFactor
  datac$ci <- datac$ci * correctionFactor
  
  return(datac)
}

### machine learning utils ###
# @see: source(../../rlsa/rlsa_matrix.R)
# @TODO: clean up the recipe functions svm.train, glm.train, ada.train, etc.
rmse <- function(obs, predval) sqrt(mean((obs-predval)^2))
# report performance
test_classification <- function (test, predmodel, do.print=T, mtype='svm') {
  if ( has.str(mtype,'svm') ) {
    test$pred <- predict(predmodel, test[,-1])
    if ( has.str(mtype,'regr') ) printf('RMSE=%.4f',rmse(test$like,test$pred))
  } else {
    test$prob <- predict(predmodel, test[,-1], type="response")
    test$pred <- test$prob>=0.5
  }
  outcome <- table(test$like,test$pred)
  ## print(outcome)
  TN <- outcome[1,1]
  FN <- outcome[2,1]
  FP <- outcome[1,2]
  TP <- outcome[2,2]
  precision <- if (TP + FP ==0) { 1 } else { TP / (TP + FP) }
  recall <- TP / (TP + FN)
  accuracy <- (TP + TN) / (TN + FN + FP + TP)
  defects <- (TP + FN) / (TN + FN + FP + TP)
  f1 <- 2*(precision*recall)/(precision+recall)
  if (do.print) cat(sprintf('#samples=%d\ndeft=%.2f,prec=%.2f,recl=%.2f,accu=%.2f,f1=%.2f\n',length(test$pred),defects,precision,recall,accuracy,f1))
  return (c(defects, precision, recall, accuracy,f1))
}

### ggplot2 functions ###
## @see: source(../../rplot/rplot_ggplot.R)

stat_sum_df <- function(DF=DF,fun, geom="crossbar", clr='red',width=0.01,...) { 
  stat_summary(data=DF,aes(x=grp,y=y),fun.data=fun, geom=geom, colour=clr,width=width, ...) 
}   
stat_sum_single <- function(DF=DF,fun, geom="point", ...) { 
  stat_summary(data=DF,aes(x=grp,y=y),fun.y=fun, colour="red", geom=geom, size = 3, ...) 
}   

# initialize ggplot with blank them instead of default gray background
rplot_init <- function(liblist=c(),linecolor='gray90') {
  suppressPackageStartupMessages( require(ggplot2,quietly=T) )  
  theme_update(panel.background=theme_blank(), 
               panel.grid.major=theme_line(colour = linecolor),
               panel.border=theme_blank())
  if ('MASS' %in% liblist) suppressPackageStartupMessages( require(MASS,quietly=T) )  
  if ('gplots' %in% liblist) suppressPackageStartupMessages( require(gplots,quietly=T) )  
}

rplot_with <- function(p,opt=list(with='p')) {
  if ( grepl('(p|point)', opt$with) ) p <- p + geom_point()
  else if ( grepl('(o|circle)', opt$with) ) p <- p + geom_point(shape=1)
  else if ( grepl('(sq|square)', opt$with) ) p <- p + geom_point(shape=0)
  else if ( grepl('(tri|triangle)', opt$with) ) p <- p + geom_point(shape=2)
  if ( grepl('(l|line)', opt$with) ) p <- p + geom_line()   
  else if ( grepl('dash', opt$with) ) p <- p + geom_line(linetype='dashed')   
  else if ( grepl('dot', opt$with) ) p <- p + geom_line(linetype='dotted')   
  p
}  

# plot with log-scale on xy
rplot_log <- function(p,opt=list(log='xy')) {
  has.label = F
  if (has.str(opt$log,'x')) {
    if ( grepl('(lnX|xe|xn)', opt$log, ignore.case=T) ) p <- p + scale_x_log(name=opt$xlab)
    if ( grepl('(log2X|lg2X|l2x|x2)', opt$log, ignore.case=T) ) p <- p + scale_x_log2(name=opt$xlab)
    else p <- p + scale_x_log10(name=opt$xlab) # (log10X|lg10X|l10x|lx|x10)
    has.label = T
  }
  if (has.str(opt$log,'y')) {
    if ( grepl('(lnY|ye|yn)', opt$log, ignore.case=T) ) p <- p + scale_y_log(name=opt$ylab)
    if ( grepl('(log2Y|lg2Y|l2y|y2)', opt$log, ignore.case=T) ) p <- p + scale_y_log2(name=opt$ylab)
    else p <- p + scale_y_log10(name=opt$ylab) # (log10Y|lg10Y|l10y|ly|y10)
    has.label = T
  }
  if (!has.label) p <- rplot_label(p,opt)
  p
}

rplot_label <- function(p,opt=list(xlab='x',ylab='y')) {
  p <- p + scale_x_continuous(name=opt$xlab)
  p <- p + scale_y_continuous(name=opt$ylab)    
  p
}

# output plot
rplot_output <- function(p,opt=list(tmpimg='test.png',opencmd='open')) {
  if (!is.null(opt$title)) p <- p + opts(title=opt$title)
  png(opt$tmpimg)
  print(p)
  dev.off()
  system(sprintf('%s %s',opt$opencmd,opt$tmpimg))  
}

self_test_utils <- function() {
  lib_init(c('MASS','Hmisc','Matrix'))
  rplot_init()
  
  x <- c(1:4,0:5,11)
  which.min(x); which.max(x); which.median(x)

  x <- cbind(x1 = 3, x2 = c(4:1, 2:5))
  rowSums(x); colSums(x); rowMeans(x); colMeans(x); rowVars(x); colVars(x)
  x <- cbind(x1 = c(5:2, 1:4), x2 = c(4:1, 2:5))
  corstars(x)
  
  x1 = c(5:20, 1:40); x2 = c(5:10, 1:50)
  corstar(x1,x2)  
  
  a2i <- load.dict('test/les2num.txt'); print(keys(a2i)); print(values(a2i))
  print( a2i[['Wyden:D:OR:Sen']] )
  print( has.key('Webb:D:VA:Sen',a2i) )
  print( all( has.key( c('Wicker:R:MS:Sen','Wyden:D:OR:Sen','abc'), a2i ) ) )
  
  X <- data.frame(x1 = c(6:20, 1:40), x2 = c(rep(1,20), rep(2,35)))
  Y <- summarySE(X, measurevar="x1", groupvars=c('x2'))
  print(Y)
}


# @see: http://thetarzan.wordpress.com/2011/05/24/summary-statistics-function-in-r-sumstats/

# mean.k function
mean.k=function(x) {
    if (is.numeric(x)) round(mean(x, na.rm=TRUE), digits = 2)
    else "N*N"
}

# median.k function
median.k=function(x) {
    if (is.numeric(x)) round(median(x, na.rm=TRUE), digits = 2)
    else "N*N"
}

# sd.k function
sd.k=function(x) {
    if (is.numeric(x)) round(sd(x, na.rm=TRUE), digits = 2)
    else "N*N"
}

# min.k function
min.k=function(x) {
    if (is.numeric(x)) round(min(x, na.rm=TRUE), digits = 2)
    else "N*N"
}

# max.k function
max.k=function(x) {
    if (is.numeric(x)) round(max(x, na.rm=TRUE), digits = 2)
    else "N*N"
}

###########################################################

# sumstats function #

sumstats=function(x) {    # start function sumstats
    sumtable = cbind(as.matrix(colSums(!is.na(x))),
                     sapply(x,mean.k),
                     sapply(x,median.k),
                     sapply(x,sd.k),
                     sapply(x,min.k),
                     sapply(x,max.k))
    sumtable=as.data.frame(sumtable)
    names(sumtable)=c("Obs","Mean","Median","Std.Dev","min","MAX")
    sumtable
}						# end function sumstats

# conver ts object to Date object, used for ggplot plotting timeseries
#@see http://stackoverflow.com/questions/2219626/using-ggplot-how-to-have-the-x-axis-of-time-series-plots-set-up-automatically
ts2dates <- function(ts){
    dur<-12%/%frequency(ts)
    years<-trunc(time(ts))
    months<-(cycle(ts)-1)*dur+1
    yr.mn<-as.data.frame(cbind(years,months))
    dt<-apply(yr.mn,1,function(r){paste(r[1],r[2],'01',sep='/')})
    as.Date(dt,tz='UTC')
}
