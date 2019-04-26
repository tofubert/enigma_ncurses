#!/bin/bash
lpr -P zj-58 -o orientation-requested=5 -o cpi=1.7 -o lpi=1.1 -o page-right=0 /home/pi/enigma_ncurses/printer/foo
#convert -size 100x200 xc:White -gravity Center -weight 350 -pointsize 100 -annotate 0 "$1\n$2" -rotate "180" oil.png  && lpr -o orientation-requested=5 -P zj-58 ./oil.png 
