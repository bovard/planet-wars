#!/bin/bash
   for i in {1..5}
   do
      RES=`./tcp 72.44.46.68 995 Meatkat15.3 -p Tinarox123 ./old_versions/v15_3/MyBot.pyo`
      echo "Game: $i" 
      echo "$RES"
   done
