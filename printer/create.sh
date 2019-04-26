#!/bin/bash
convert -size 200x400 xc:White -gravity Center -weight 700 -pointsize 200 -annotate 0 "$1\n$2" -rotate "180" oil.png  && lpr -o orientation-requested=5 -P zj-58 ./oil.png 
