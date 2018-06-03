#!/bin/bash

pdflatex -shell-escape node_diagram.tex
convert node_diagram.pdf node_diagram.png

# cleanup
rm *.aux
rm *.log

# remove also pdf
rm *.pdf
