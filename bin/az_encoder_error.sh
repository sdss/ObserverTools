#!/bin/bash
#------------------------------------------------------------------------------
#
# Computer encoder errors on both AZ encoders. 
#  Kaike Pan, APO.
#------------------------------------------------------------------------------

echo -n 'Enter mjd:'
read mjd
zippedFilename="/data/logs/mcp/mcpFiducials-"$mjd".dat.gz"
if [[ -f zippedFilename ]]; then
    filename=zippedFilename;
    gzip -d --stdout ${filename} > temp.txt
    tail -500  temp.txt | grep AZ_FIDUCIAL > temp.txt
else
    filename="/data/logs/mcp/mcpFiducials-"$mjd".dat"
    tail -500  ${filename} | grep AZ_FIDUCIAL > temp.txt
fi
while read -r dump dump ID exp1 exp2 pos1 pos2 dump; do
#echo $ID $exp1 $exp2
let error1=$pos1-$exp1
let error2=$pos2-$exp2
echo "ID="$ID "two encoder errors are  " $error1 $error2
done < temp.txt
rm temp.txt
