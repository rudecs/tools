#!/bin/bash

THRESHOLD="1"
SLEEP="10"
WORKDIR="~root/ki"
export PATH=$PATH:/opt/linuxki

# Remove stop-file
if [ -e $WORKDIR/stop ]; then
    rm -f $WORKDIR/stop
fi

# Start daemon
while :; do
    if [ -f $WORKDIR/stop ]; then
        break
    fi
    LA=`cat /proc/loadavg|cut -d "." -f 1`
    if [ "${LA}" -ge "${THRESHOLD}" ]; then
	date > $WORKDIR/stop
        runki -f
    fi
    sleep $SLEEP
done

exit 0

