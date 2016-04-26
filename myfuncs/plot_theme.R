# plot_theme.R - define the white background theme used in ggplot
# @author: Yu-Ru Lin
# @date: Dec 8, 2012
# usage: 
#   source('../../myfuncs/plot_theme.R')
#   modify the settings of font/color as necessary

require(Matrix);require(MASS);require(igraph); require(RColorBrewer); require(ggplot2)
library(scales) 
theme_set( theme_bw( base_family="Helvetica")) # the font changign doesn't work for Mac
theme_update(plot.title = element_text( size=11,vjust=1,face='bold'),
             axis.title.x = element_text( size=12),
             axis.title.y = element_text( size=12,angle=90 ),
             axis.text.x = element_text( size=10),
             axis.text.y = element_text( size=10,hjust=1 ))

# usage:
#   p = ggplot(...)
## plot the result
#   print(p); return 
## plot the result into image file
#   opt = NULL;
#   opt$output = sprintf('%s/scatter_predebate_%s_%s.pdf',outputpath_fig,xlab,ylab_)
#   opt$width = 360; opt$height=360;
#   rplot_output(p,opt)    
rplot_output <- function(p,opt) {
    print(opt$output)
    try( p <- p + theme(axis.ticks.margin = unit(.1, "cm")) ) #skip if it doesn't work
    if (!is.null(opt$title)) p <- p + theme(title=opt$title)
    if (!is.null(opt$legend)) p <- p + labs(colour=opt$legend,fill=opt$legend)
    ext <- gsub("(.*)\\.([^([:space:]|.)]+)$",'\\2',opt$output)
    if ( grepl('png', ext, ignore.case=T) ) png(opt$output,width=opt$width,height=opt$height) # in pixel
    else if ( grepl('pdf', ext, ignore.case=T) ) pdf(opt$output,width=opt$width/80,height=opt$height/80) # in inches
    else if ( grepl('(jpg|jpeg)', ext, ignore.case=T) ) jpeg(opt$output,width=opt$width,height=opt$height)
    else if ( grepl('bmp', ext, ignore.case=T) ) bmp(opt$output,width=opt$width,height=opt$height)
    else {
        cat('error: unknow image format:',ext,'.\n'); q(status=1) 
    }
    print(p)
    dev.off()
}