#!/bin/sh
PROJECT_PATH=/home/codezero/collect_server

# source $PROJECT_PATH/cron_env/bin/activate
/usr/bin/python2.7 $PROJECT_PATH/TrendDetectorFB/collect_data.py -c $PROJECT_PATH/TrendDetectorFB/config.cfg
