#!/bin/bash

if [ -z "$THRESHOLD" ]; then
    THRESHOLD="20"
fi
SLEEP="10"
WORKDIR="/opt/de/linuxki"
export PATH=$PATH:/opt/linuxki

#Create workdir
if [ ! -d $WORKDIR ]; then
    mkdir -p $WORKDIR
fi

# Remove stop-file
if [ -e $WORKDIR/stop ]; then
    rm -f $WORKDIR/stop
fi

# Start daemon
while :; do
    if [ -f $WORKDIR/stop ]; then
        break
    fi
    echo $THRESHOLD
    LA=`cat /proc/loadavg|cut -d "." -f 1`
    if [ "${LA}" -ge "${THRESHOLD}" ]; then
	
	date > $WORKDIR/stop
	echo "THRESHOLD: $THRESHOLD" >> $WORKDIR/stop
        runki -f
    fi
    sleep $SLEEP
done

exit 0

