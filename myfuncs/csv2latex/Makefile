all: table.pdf

table.pdf : table.tex
  pdflatex $< 

table.tex : names.csv table_template.tex csv2latex.py
  python csv2latex.py


