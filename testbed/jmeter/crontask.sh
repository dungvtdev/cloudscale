#!/bin/sh

echo Start new cron task at $(date) >> cron.log

sh /root/cloudscale/testbed/jmeter/runtest.sh