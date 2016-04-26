# connect_mysql.R - get data from mysql table
# @author: Yu-Ru Lin
# @date: Dec 24, 2013

library(RMySQL)

dbuser = 'yuru'; dbpass = 'yuru123'; dbname = 'db_debate'; dbhost = 'localhost'

load.data <- function(sqlstr = NULL,print.dim=F,print.data=F,disconnect.all=T,print.tables=F,db.name=dbname) {
  if (disconnect.all) {
    cons = dbListConnections(MySQL())
    for(con in cons) dbDisconnect(con)    
  }
  
  con = dbConnect(MySQL(), user=dbuser, password=dbpass, dbname=db.name, host=dbhost)
  if (print.tables) print(dbListTables(con))
  if (is.null(sqlstr)) {
    sqlstr = 'select * from mon201210 limit 20;'    
  } else cat('q:',sqlstr,'\n')
  rs = NULL;
  rs = dbSendQuery(mydb, "SET CHARACTER SET 'utf8'")
  res = try( (rs = dbSendQuery(con, sqlstr)) )
  if (inherits(res, "try-error")) {
    if (!is.null(rs)) {
      dbClearResult(rs)
      dbDisconnect(con)      
    }
    return(NULL)
  }
  data = fetch(rs, n=-1)
  if (print.dim) print(dim(data))
  if (print.data) print(head(data))
  #huh = dbHasCompleted(rs); print(huh)
  dbClearResult(rs)
  dbDisconnect(con)
  data
}

### main ###
# load.data(print.data=T)