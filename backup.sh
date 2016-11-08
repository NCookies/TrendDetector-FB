today=$(date +%Y%m%d)
last_week=$(date -d '-7day' +%Y%m%d)

tar cvfpz /home/codezero/trendBackup/bbs-$today.gz /home/codezero/collect_server/TrendDetectorFB/input_data_set.csv

rm /home/codezero/trendBackup/bbs-$last_week.gz
