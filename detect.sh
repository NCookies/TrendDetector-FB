PROJECT_PATH=/home/codezero/collect_server/TrendDetectorFB
input_file=$PROJECT_PATH/input_data_set.csv

cd $PROJECT_PATH

# python trend_analyze_many.py -c config.cfg -i $input_file -r rebinned.json -o analyze.json -p analyze.json --rebin

python trend_analyze_many.py -c config.cfg -i $input_file -r rebinned.json -o analyze.json -p analyze.json --rebin

python trend_analyze_many.py -c config.cfg -i $input_file -r rebinned.json -o analyze.json -p analyze.json --analysis

python trend_analyze_many.py -c config.cfg -i $input_file -r rebinned.json -o analyze.json -p analyze.json --plot
