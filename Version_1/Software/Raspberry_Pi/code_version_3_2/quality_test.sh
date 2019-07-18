#!/bin/bash

#
#   This script is used to test video settings
#   Used to fine tune camera parameters
#

# Select video lenght
len='60000'

# Select bitrate
bitrs='10000000 12000000 15000000'
# Select fps
modes='1 5'
# Select profile
profs='baseline main high'

for br in $bitrs
do
    echo ""
    echo --bps: $br
    for md in $modes
    do
        echo ----mode: $md
        for pf in $profs
        do
            echo ------prof: $pf
            # Command
            raspivid -t 60000 -pf $pf -o /home/pi/Video/$br_$md_$pf.h264 -a 12 -md $md -rot 180 -fps 30 -b $br -ae 32,0xff,0x808000 -ih -a 1024
        done
    done
done

echo ""
echo "Downloading ..."
# Command
rsync -h --progress /home/pi/Video/*.h264 arthur@192.168.2.31:/home/arthur/Projects/Underwater-POV-Camera-Tag/Data/Q_Test
echo "Finished"

echo ""
echo "Converting ..."
# Command
ssh arthur@192.168.2.31 ./home/arthur/Projects/Underwater-POV-Camera-Tag/Data/Q_Test/convert.sh
echo "Done"