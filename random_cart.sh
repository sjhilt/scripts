#!/bin/sh
# Author: Stephen Hilt
# load a random cartrage on the leapster GS from .iso files
# these can be made from the actual cartrages so you don't 
# have to carry all of them around. this randomizes to keep
# the kids happier :) 
#################################
# get the length of the number of files that are .iso
# in /LF/Bulk
size=`ls -l /LF/Bulk | grep .iso | wc -l`
# find a random numbr
ran_num=`awk 'BEGIN{srand();print int(rand()*(9-1))+1 }'`
# unmount cartridge
umount /LF/Cart
# part of the leapster commands
cnotify 0
# set counter to 0
counter=0
# for loop to select the .iso file
for i in `ls /LF/Bulk/ | grep .iso`;
do
        if [ $counter -eq $ran_num ]; then
                mount -o loop /LF/Bulk/$i /LF/Cart/
                cnotify 3
        fi
        counter=$((counter+1))
done
