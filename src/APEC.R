# load_apec.R - load and explore the apec data

Sys.setenv(NOAWT = "true")  ## work around for the stemmer issue
library(rJava)
library(tm)
library(NMF)
# library(lsa)
library(ggplot2)
library(RMySQL)
library(RWeka)
library(igraph)
suppressWarnings(source('myfuncs/utils.R'))
suppressWarnings(source('myfuncs/plot_theme.R'))
suppressWarnings(source('myfuncs/itall.R'))

pause <- function(s=NULL) {
  if (!is.null(s)) cat(s,'\n')
  readline(prompt = "Pause. Press <Enter> to continue...")
}

dbuser = 'yuru'; dbpass = 'yuru123'; db.name = 'APEC'; dbhost = 'localhost'

load.data <- function(sqlstr = NULL) {
  con = dbConnect(MySQL(), user=dbuser, password=dbpass, dbname=db.name, host=dbhost)
  #   print(dbListTables(con))
  rs = dbSendQuery(con, "SET CHARACTER SET 'utf8'")
  if (is.null(sqlstr)) {
    #     sqlstr = 'select count(*) from A;'
    sqlstr = 'select * from A limit 20;'    
  }
  rs = dbSendQuery(con, sqlstr)
  data = fetch(rs, n=-1)
  print(dim(data))
  #   print(data)
  dbClearResult(rs)
  dbDisconnect(con)
  data
}

xlab_='time (UTC)'
ylab_='value'
title_=''

plot.volume <- function(DF, xlab=xlab_,ylab=ylab_,annotext='abc') {
  print(dim(DF))
  print(head(DF))
  print(sumstats(DF))
  
  DF$time <- as.POSIXct(DF$time,"UTC")
  
  xmin = min(DF$time)
  ymax = max(DF$cnt)
  p = ggplot(DF, aes(x=time,y=cnt,color=country))+
    geom_line(size=.7)+
    #     stat_smooth(method='loess',span = 0.1)+
    #     scale_y_continuous(name=ylab,limits=c(-0.15,0.25))+
    scale_x_datetime(name=xlab)
  #     annotate('text', x=xmin+3600*1, y=0.24, label=annotext)
  print(p)
  
}

text2corpus <- function(text, verbose=F, remove.stopwords=F, stemming=F) {
  corpus = Corpus(VectorSource(text))
  corpus = tm_map(corpus, tolower)  ## convert text to lower case
  if (verbose) inspect(corpus[1:3])
  
  # remove custom stopwords
  my_stopwords = c('n','r')
  corpus = tm_map(corpus, removeWords, my_stopwords)
  
  corpus = tm_map(corpus, removePunctuation)  ## remove punctuations
  if (verbose) inspect(corpus[1:3])
  corpus = tm_map(corpus, removeNumbers)  ## remove numbers
  if (verbose) inspect(corpus[1:3])
  
  if (remove.stopwords) {
    corpus = tm_map(corpus, function(x) removeWords(x, stopwords("english")))  ## remove stopwords
    if (verbose) inspect(corpus[1:3])    
  }
  if (stemming) {
    corpus = tm_map(corpus, stemDocument, language = "english",mc.cores=1)  ## stemming
    if (verbose) inspect(corpus[1:3])  ##encounter encoding issues.    
  }
  print(corpus) ## print summary of the corpus
  corpus
}

corpus2matrix <- function(corpus,ngram=0,fname='1',use.dict=T,lo.bound=0.05,hi.bound=0.5) {
  #   control=list(wordLengths=c(1,Inf)) 
  control=list(wordLengths=c(1,Inf),
               bounds=list(global=c(floor(length(corpus)*lo.bound), floor(length(corpus)*hi.bound) ))) 
  if (ngram) {
    BigramTokenizer <- function(x) NGramTokenizer(x, Weka_control(min = ngram, max = ngram))
    control$tokenize = BigramTokenizer
  } 
  if (use.dict) {
    ifilename = sprintf('./gnews/output/all/dict.rda')
    dict = load.RData(ifilename)
    cat('#dict',length(dict),'\n')
    control$dictionary=dict
  }
  if (0) {
    d = c('a lot of','a meeting with')
    d = c('meeting','obama')
    control$dictionary=d
    print(control)
  }
  cat('...creating term-doc matrix...\n')
  td.mat = TermDocumentMatrix(corpus,control=control)    
  print(td.mat)
  if (!is.null(fname)) {
    ofilename = sprintf('./gnews/output/all/tdmat-%s-ngram%d.rda',fname,ngram)
    save.RData(td.mat,ofilename)    
  }
  print(dim(td.mat))
  cat('dim of term-doc matrix:',dim(td.mat),'\n')
  td.mat
}

get.binary.matrix <- function(mat) {
  ifelse(mat>0, 1, 0) ## binary matrix
}

get.tfidf.matrix <- function(mat) {
  lw_tf(mat) * gw_idf(mat)  ## tf-idf weighting
}

dtm.to.sm <- function(dtm) {
  sparseMatrix(i=dtm$i, j=dtm$j, x=dtm$v,
               dims=c(dtm$nrow, dtm$ncol))
} 

load.data.in.range <- function(start.date="2013-10-01",end.date="2013-10-14",use.cache=T) {
  if (use.cache) {
    ifilename = sprintf('./gnews/output/all/data.rda')
    text = load.RData(ifilename) 
    ifilename = sprintf('./gnews/output/all/tdmat.rda')
    td.mat = load.RData(ifilename) 
  }
  else {
    text = load.data(sqlstr = sprintf('select ID, COUNTRY, ENG, TIMESTAMP from A where datediff(TIMESTAMP,"%s")>=0 and datediff(TIMESTAMP,"%s")<0',start.date,end.date))    
    ofilename = sprintf('./gnews/output/all/data.rda')
    save.RData(text,ofilename)    
    
    corpus = text2corpus(text$ENG,remove.stopwords=T,stemming=F)
    td.mat = corpus2matrix(corpus,ngram=0,fname=NULL,use.dict=F)      
    ofilename = sprintf('./gnews/output/all/tdmat.rda')
    save.RData(td.mat,ofilename)    
  }
  smat = dtm.to.sm(td.mat)
  tf = rowSums(smat); names(tf) = rownames(td.mat)
  print(sort(tf,decreasing=T)[1:10])
  smat
}

load.data.in.range.outlet <- function(start.date="2013-10-01",end.date="2013-10-14",use.cache=T) {
  if (use.cache) {
    ifilename = sprintf('./gnews/output/all/outlet.rda')
    text = load.RData(ifilename) 
  }
  else {
    start.date="2013-10-01" 
    end.date="2013-10-14"
    text = load.data(sqlstr = sprintf('SELECT source, country, count(id) FROM `A` where datediff(TIMESTAMP,"%s")>=0 and datediff(TIMESTAMP,"%s")<0 group by SOURCE',start.date,end.date))    
    ofilename = sprintf('./gnews/output/all/outlet.rda')
    save.RData(text,ofilename)      
  }
}

run.nmf <- function(mat,ks=2:6,k=0) {
  # V ~ WH' V is an n x p matrix W = n x r term feature matrix H = r x p doc
  # feature matrix
  set.seed(12345)
  if (k==0) { ## estimate best rank (k)
    estim.r = nmf(mat, ks, nrun = 10, seed = 123456)    
       plot(estim.r)
  } 
  if (1) {
    ptm = proc.time()
    res = nmf(mat, k, 'lee')  # lee & seung method
    print(proc.time() - ptm)
    ofilename = sprintf('./gnews/output/all/nmf_res_k%d.rda',k)
    save.RData(res,ofilename)    
    
    V.hat = fitted(res)
    print(dim(V.hat))  ## estimated target matrix
    
    w = basis(res)  ##  W  term feature matrix matrix
    print(dim(w))  # n x r 
    
    h = coef(res)  ## H  doc feature matrix
    print(dim(h))  #  r x p    
  }
  res 
}

explore.nmf <- function(k=0,use.cache=T,plot.heatmap=T,plot.wordcloud=T) {
  library(wordcloud)
  
  if (use.cache) {
    ifilename = sprintf('./gnews/output/all/tdmat.rda')
    td.mat = load.RData(ifilename) 
    words = rownames(td.mat)

    ifilename = sprintf('./gnews/output/all/nmf_res_k%d.rda',k)
    res = load.RData(ifilename)
  }

  V.hat = fitted(res)
  print(dim(V.hat))  ## estimated target matrix
  
  w = basis(res)  ##  W  term feature matrix matrix
  print(dim(w))  # n x r 
  
  h = coef(res)  ## H  doc feature matrix
  print(dim(h))  #  r x p
#   print(colSums(h))
  
  if (plot.heatmap) {
    #   consensusmap(res)
    #   basismap(res,Colv="euclidean")
    coefmap(res,Colv="basis")
    pause()    
  }
  if (plot.wordcloud) {
    for (ki in 1:k) {
      cat('cluster',ki,':\n')
      word.prob = w[,ki]; #print(word.prob)
      names(word.prob) = words
      idx = order(-word.prob)[1:100]
      # print(word.prob[idx])
      wc = data.frame(word = names(word.prob[idx]), freq = word.prob[idx])
      wordcloud(wc$word, wc$freq, max.words = 100, random.order=F, rot.per=0)  
      pause()
    }    
  }
  res
}

doc2country.matrix <- function(use.cache=T) { #revised into time period verison
  if (use.cache) {
    ifilename = sprintf('./gnews/output/all/data.rda')
    text = load.RData(ifilename) 
    ifilename_p1 = sprintf('./gnews/output/P3/data.rda')
    text_p1 = load.RData(ifilename_p1) 
  }
  country.list = unique(text$COUNTRY)
  print(head(country.list))
  doc2country = match(text$COUNTRY,country.list)
  d2c.mat = matrix(0, nrow=nrow(text_p1), ncol=length(country.list))
  
  for (i in 1:nrow(text) ) if(text[i,1] %in% text_p1[,1]) d2c.mat[which(text_p1==text[i,1]),doc2country[i]]=1
  colnames(d2c.mat) = country.list
 #  print(d2c.mat[1:3,]); print(dim(d2c.mat))
  d2c.mat
}

doc2cluster.matrix <- function(k=6,use.cache=T,plot.heatmap=F) {
  k=6
  if (use.cache) {
   
    ifilename = sprintf('./gnews/output/all/nmf_res_k%d.rda',k)
    res = load.RData(ifilename)   
    ifilename_t = sprintf('./gnews/output/all/data.rda')
    text_t = load.RData(ifilename_t)     
    ifilename_p1 = sprintf('./gnews/output/P3/data.rda')
    text_p1 = load.RData(ifilename_p1) 
  }  
  h = coef(res)  ## H  doc feature matrix (r x p)
  h.mat = matrix(0, k, ncol=nrow(text_p1))
  for (i in 1:ncol(h) ) {
     if((text_t[i,1] %in% text_p1[,1])){
        #print(which(text_p1==text_t[1555,1]))
        h.mat[,which(text_p1==text_t[i,1])] = h[,i]
     }
  }
  h <- h.mat
  
  print(dim(h))  #  k x nDoc 
  print(colSums(h))
  csum = colSums(h) # 1 x nDoc; the total cluster prob. of each doc
  d2c = apply(h, 1, function(x) x / csum) # for each row, divide by the total cluster prob.;  nDoc x k; each row sum to one
  if (plot.heatmap) {
    dominant.clust = apply(d2c, 1, which.max)
    image(d2c[order(dominant.clust),])    
  }
  colnames(d2c) = paste('M',1:ncol(d2c),sep='')
  d2c # nDoc x k
#   print(m[1:3,])
#   print(rowSums(m))
}

doc2cluster.matrix.outlet <- function(k=6,use.cache=T,plot.heatmap=F) {
  mydb = dbConnect(MySQL(), user='highman', password='mysql123', dbname='GNews', host='192.168.0.3')
  start.date="2013-10-01" 
  end.date="2013-10-14"
    
  sqlstr = sprintf('SELECT source, country, count(id) as c FROM `A` where datediff(TIMESTAMP,"%s")>=0 and datediff(TIMESTAMP,"%s")<0 group by SOURCE having c >5',start.date,end.date)
  rs = dbSendQuery(mydb, "SET CHARACTER SET 'utf8'")
  rs = dbSendQuery(mydb, sqlstr) 
  res = fetch(rs, n=-1)  
  
  res[,1] <- reorder(res[,1], -res[,3])
  p4 <- ggplot(res, aes(res[,1], res[,3]))
  p4 <- p4 + geom_bar(stat = "identity") + geom_point() 
  p4 <- p4 + labs(x = "Countries",y = "News volume",title = "News frequency bar by theme 測試")
  p4 <- p4 + theme(plot.title = element_text(size = rel(2)))
  p4 <- p4 + theme(text = element_text(size=16), axis.title.x = element_text(size=12), axis.title.y = element_text(size=30)) 
  p4 <- p4 + theme(axis.text.x = element_text(size=8, angle = 90, hjust = 1), axis.text.y = element_text(size=20))
  p4
}

doc2cluster.matrix.theme <- function(k=6,use.cache=T,plot.heatmap=F) {
  #if (use.cache) {
  k=6
    ifilename = sprintf('./gnews/output/all/nmf_res_k%d.rda',k)
    res = load.RData(ifilename)    

    ifilename = sprintf('./gnews/output/all/data.rda')
    text = load.RData(ifilename) 
  #}  
  h = coef(res)  ## H  doc feature matrix (r x p)
  print(dim(h))  #  k x nDoc 
 
  uni<-unique(substr(text[, 4], 0, 10))
  cluster2date.mat <- array(0, c(length(uni)*k,3))
  for (i in 1:nrow(text) ) {
    #n <- (which(uni == substr(text[i, 4], 0, 10)) * k ) - 6 + which.max(h[,i])
    #cluster2date.mat[n,3] <- as.numeric(cluster2date.mat[n,3]) +1
    #cluster2date.mat[n,2] <- which.max(h[,i])
    #cluster2date.mat[n,1] <- substr(text[i, 4], 0, 10)
    for (j in 1:k ) {
      n <- (which(uni == substr(text[i, 4], 0, 10)) * k ) - 6
      if(which.max(h[,i])==j) cluster2date.mat[n+j,3] <- as.numeric(cluster2date.mat[n+j,3]) +1
      cluster2date.mat[n+j,2] <- j
      cluster2date.mat[n+j,1] <- substr(text[i, 4], 0, 10)
    }
  }

  t <- as.data.frame(cluster2date.mat,stringsAsFactors=F)
  as.numeric(t$V3)
  #frequency by country
  p3 <- ggplot(t, aes(V1, as.numeric(V3), group=V2, colour=V2))
#  p3 <- p3 + geom_line(aes(linetype=V2), size = 1.5) + geom_point(aes(shape=V2), size = 4) + scale_shape(solid=FALSE)
  p3 <- p3 + geom_line(size = 2)
  p3 <- p3 + labs(colour ="Theme",shape="themes", x = "News Date",y = "News Frequency",title = "News Frequency of Themes")
  p3 <- p3 + theme(plot.title = element_text(size = rel(1)))
  p3 <- p3 + theme(text = element_text(size=14), axis.title.x = element_text(size=14), axis.title.y = element_text(size=14), axis.text.x = element_text(angle = 90, hjust = 1, size=12), axis.text.y = element_text(size=12)) 
  p3
}

doc2cluster.matrix.theme.bar <- function(k=6,use.cache=T,th=1) {
  if (use.cache) {
  ifilename = sprintf('./gnews/output/all/nmf_res_k%d.rda',k)
  res = load.RData(ifilename)    
  
  ifilename = sprintf('./gnews/output/all/data.rda')
  text = load.RData(ifilename) 
  }  
  h = coef(res)  ## H  doc feature matrix (r x p)
  print(dim(h))  #  k x nDoc 
  
  uni<-unique(text[, 2])
  cluster2date.mat <- array(0, c(length(uni),2))
  for (i in 1:nrow(text) ) {
    theme = which.max(h[,i])
    if(theme == th){
      for (j in 1:length(uni)) {
        if(text[i, 2] == uni[j]){
           n <- which(uni == text[i, 2])
           cluster2date.mat[n,2] <- as.numeric(cluster2date.mat[n,2]) +1
        }
        cluster2date.mat[j,1] <- uni[j]
      }
    }
  }
  
  t <- as.data.frame(cluster2date.mat,stringsAsFactors=F)
  t$V3 <- reorder(t$V1, -as.numeric(t$V2))
  p4 <- ggplot(t, aes(V3, as.numeric(V2)))
  p4 <- p4 + geom_bar(stat = "identity") + geom_point() + geom_text(aes(label=as.numeric(V2)),size=20,colour="red")
  p4 <- p4 + labs(x = "Countries",y = "News volume",title = paste("News frequency Bar of Theme", th))
  p4 <- p4 + theme(plot.title = element_text(size = rel(2)))
  p4 <- p4 + theme(text = element_text(size=32), axis.title.x = element_text(size=60), axis.title.y = element_text(size=60)) 
  p4 <- p4 + theme(axis.text.x = element_text(size=60, angle = 90, hjust = 1,colour="red"), axis.text.y = element_text(size=60))
  p4
}

doc2cluster.matrix.theme.news <- function(k=6,use.cache=T,th=1,limit=100) {
  if (use.cache) {
    ifilename = sprintf('./gnews/output/all/nmf_res_k%d.rda',k)
    res = load.RData(ifilename)    
    
    ifilename = sprintf('./gnews/output/all/data.rda')
    text = load.RData(ifilename) 
  }  
  h = coef(res)  ## H  doc feature matrix (r x p)
  print(dim(h))  #  k x nDoc 
  
  #cluster2date.mat <- array(0, c(20,4))
  sql = paste("(")
  for (i in 1:nrow(text) ) {
    theme = which.max(h[,i])
    if(theme == th && h[theme,i] > limit){
      print(c(text[i, 1], text[i, 2], theme, h[theme,i]))
      sql = paste(sql, text[i, 1] , ",")
    }
  }
  sql = paste(sql, ")")
  sql
}

build.country.network.from.nmf <- function(k=6,plot.heatmap=F) {
  doc2cty = doc2country.matrix()
  doc2clu = doc2cluster.matrix(k)
  cty2clu = t(doc2cty) %*% doc2clu
  cty2clu.raw = cty2clu
#   print(cty2clu)
  
  ## make row sum to one
  rsum = rowSums(cty2clu)
  cty2clu = apply(cty2clu, 2, function(x) x / rsum)
  
  if (plot.heatmap) {
    dominant.clust = apply(cty2clu, 1, which.max)
    tmp = cty2clu[order(dominant.clust),]
    image(tmp)  
#     print(tmp)
#     print(rowSums(tmp))
  }
  nr = nrow(cty2clu)
  nc = ncol(cty2clu)
  bmat = matrix(0,nrow=nr+nc,ncol=nr+nc)
  bmat[1:nr,(nr+1):(nr+nc)] = cty2clu
  node.names = c(rownames(cty2clu), colnames(cty2clu) )
  rownames(bmat) = node.names
  colnames(bmat) = node.names
#   print(bmat)
  set.seed(1001)
  g = graph.adjacency(bmat,weighted=T)
  pal = brewer.pal(9,"Oranges")
  E(g)$color = pal[ as.integer(E(g)$weight/max(E(g)$weight)*8+1) ]
  E(g)$width = E(g)$weight/max(E(g)$weight) * 10
  V(g)$color[(nr+1):(nr+nc)] = 'gray'
#   print(cbind(E(g)$color, E(g)$width) )
  l = layout.kamada.kawai
  l = layout.lgl
  l = layout.spring
  l = layout.drl(g, options=list(simmer.attraction=5)) # bipartite
#   l = layout.drl(g, options=igraph.drl.final)
#   l = layout.fruchterman.reingold (g, params =list(repulserad=1000,coolexp=10))
#   l = layout.fruchterman.reingold
#   l = layout.graphopt(g,params=list(charge=5,spring.length=1,mass=50))
  plot(g, layout=l, edge.color=E(g)$color, vertex.frame.color='blue', edge.width = E(g)$width, edge.curved=F )
  pause()
  
  l = layout.kamada.kawai
#   cty2cty = cty2clu %*% t(cty2clu)
  cty2cty = cty2clu.raw %*% t(cty2clu.raw)
  diag(cty2cty) = 0
#   print(cty2cty)  
  g = graph.adjacency(cty2cty,weighted=T,mode="undirected")
#   print(V(g))
  E(g)$color = pal[ as.integer(E(g)$weight/max(E(g)$weight)*8+1) ]
  E(g)$width = E(g)$weight/max(E(g)$weight) * 10
  E(g)$width = ifelse(E(g)$width>1,  E(g)$width ,0)
  plot(g, layout=l, edge.color=E(g)$color, vertex.frame.color='blue', edge.width = E(g)$width, edge.curved=F )
}

### main ###

## plot volume per country
if (0) {
  data = load.data(sqlstr = 'select count(ID) as cnt, COUNTRY as country, Date(TIMESTAMP) as time from A group by date(TIMESTAMP),COUNTRY')
  plot.volume(data)  
}

 mat = load.data.in.range(start.date="2013-10-01",end.date="2013-10-15",use.cache=F)
 for (ki in 2:10) run.nmf( as.matrix(mat) ,k=ki)

#load.data.in.range.outlet(start.date="2013-10-01",end.date="2013-10-15",use.cache=F)

explore.nmf(k=6)

#doc2country.matrix()
#doc2cluster.matrix()

build.country.network.from.nmf()

doc2cluster.matrix.theme()

doc2cluster.matrix.theme.bar(k=6,use.cache=T,th=1)
doc2cluster.matrix.theme.bar(k=6,use.cache=T,th=2)
doc2cluster.matrix.theme.bar(k=6,use.cache=T,th=3)
doc2cluster.matrix.theme.bar(k=6,use.cache=T,th=4)
doc2cluster.matrix.theme.bar(k=6,use.cache=T,th=5)
doc2cluster.matrix.theme.bar(k=6,use.cache=T,th=6)

doc2cluster.matrix.theme.news(k=6,use.cache=T,th=1,limit=353)
doc2cluster.matrix.theme.news(k=6,use.cache=T,th=2,limit=304)
doc2cluster.matrix.theme.news(k=6,use.cache=T,th=3,limit=268.1)
doc2cluster.matrix.theme.news(k=6,use.cache=T,th=4,limit=349)
doc2cluster.matrix.theme.news(k=6,use.cache=T,th=5,limit=150) #254
doc2cluster.matrix.theme.news(k=6,use.cache=T,th=6,limit=200)
