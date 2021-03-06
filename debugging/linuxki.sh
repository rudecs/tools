#!/bin/bash

if [ -z "$THRESHOLD" ]; then
    THRESHOLD="20"
fi
PIDFILE=/var/run/delinuxki.pid
SLEEP="10"
WORKDIR="/opt/de/linuxki"
STOPFILE="$WORKDIR/stop_`date +%d-%m-%Y_%H-%M-%S`"
export PATH=$PATH:/opt/linuxki
FLAG="0x0"
I=0

echo $$ > $PIDFILE

function runrunki() {
#    echo "$STOPFILE"
    date > $STOPFILE
    echo "THRESHOLD: $THRESHOLD" >> $STOPFILE
    runki -f
}


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
    if [ $I -gt 2 ]; then
#    if [ -f $WORKDIR/stop ]; then
        break
    fi
    LA=`cat /proc/loadavg|cut -d "." -f 1`
    if [ "${LA}" -ge "${THRESHOLD}" ]; then
	if [ "$FLAG" == "0x0" ]; then
            echo "second if"
            I=$(($I+1))
	    runrunki
	fi
	FLAG="0x1"
    else FLAG="0x0"
    fi
    sleep $SLEEP
done

rm -f $PIDFILE
exit 0

