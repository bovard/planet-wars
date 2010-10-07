#!/bin/bash
   for i in {1..100}
   do
      RES=`./tcp 72.44.46.68 995 Meatkat10.4.0 -p Tinarox123 ./old_versions/v10_4/MyBot.pyo`
      echo "Game: $i" 
      echo "$RES"
   done
