#!/bin/sh

JMETER=/root/jmeter3.2/bin
SCRIPT_PATH=/root/cloudscale/testbed/jmeter/test_step_performance.jmx

sh $JMETER/jmeter -n -t $SCRIPT_PATH -o out.jtl