.. title:: Generating LaTeX tables from CSV files

======================================
Generating LaTeX tables from CSV files
======================================

I am very committed to the idea of e `reproducibility <http://en.wikipedia.org/wiki/Reproducibility>`_. The way I understand the term is that there should be a link between the results presented in the paper and the raw data. It happens all too often that some pre-processing step essential for the results presented in the paper is modified slightly during the preparation of the manuscript, but the figures, tables and statistics are not updated accordingly.

Let's take for example a table. Tables contain usually some pre-processed data from the experiments or simulations. The standard workflow to produce a table is to import data from a database or a file into a word processor and then to format it by adding borders, meging cells etc. The problem arises when one wants to modify the data within the table (for example, change units, significance level or pre-processing parameters). In such a case a repetition of the complete workflow is necessary, which may be very time consuming (esp. when the manuscript is still in its early state or the reviewers ask for more analyses/experiments).

My solution to the problem is to use LaTeX templates which are filled-in with data from `CSV <http://en.wikipedia.org/wiki/Comma-separated_values>`_ (comma seperated values) file, which is a simple and common text data format used by many applications. LaTeX files can be easily converted to HTML, PDF or even DOC (the last option is not 100% functional yet, but I am working on it), which then can be copy-pasted into your document or attached as a supplementary data.

You will need:

* LaTeX environment (for example TexLive or TeTeX for Linux/Mac or MicTex for Windows),
* Python >= 2.6 (earlier versions may work but I haven't tested them),
* templating system: a Python module which can render a final LaTeX file from a template. In the example I use `Django <http://www.djangoproject.com/>`_ template system, but Cheetah or Jinja can be also used.
* CSV file: it can contain anything from your shopping list through simulations result to data from experiments.

The CSV file may look like that:

.. literalinclude:: names.csv

Here is how to generate a PDF from a LaTeX file from this (or similar) CSV file.

1. Create a LaTeX template.
   
   Here you will need some working knowledge of LaTeX, but you can start with the following template:

   .. literalinclude:: table_template.tex
      :language: tex
 
   If you are familiar with LaTeX you might have notice the strange
   commands inside {% ... %} brackets -- these are Django template
   commands (for a comprehensive list see the 
   `Django documentation <http://docs.djangoproject.com/en/dev/ref/templates/builtins/>`_).
   The syntax is similar to (reduced) Python, so we have for loops
   which iterate over rows and columns and conditional statements to
   make sure that we do not have too many column separators (LaTeX
   does not like it). The ``head`` and ``table`` variables contain the data
   which is filled into the template. In order to define them we need
   a little bit of Python code. 

   
2. Import the CSV file and render the template to obtain a final LaTeX
   file.  This iswhere the actual conversion from CSV to LaTeX occurs.
   In Python it is extremly simple (I may be biased here, though):

   .. literalinclude:: csv2latex.py
   
     
3. Generate a PDF output from the generated LaTeX file.
   Once you have the final LaTeX file, you can use LaTeX system to
   generate output in a plenty of format. For example to obtain a PDF
   file, just call from a command line:

   ::

      pdflatex table.tex

   If everything went fine a PDF file should be created in your current directory. If not, something is probably wrong with your template or your LaTeX installation.
   
4. All of the above steps can be of course automated with a simple Makefile.
   This is an optional step for those of readers who are crazy about
   reproducibility (like me!).

   .. literalinclude:: Makefile
      :language: make

   Now, whenever your data change, it is enough to call ``make`` to get a nicely formatted PDF table! 

All of the source files and generated output are available for download.

*Update*: There is also a tool which converts CSV to LaTeX (csv2latex) I
haven't tested it, but it seems that it does not offer the flexibility
the templating system gives you, but as always everything comes at
some cost (in case of the template system cost=dependencies ;)).

