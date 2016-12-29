fullfile=$1
filename=$(basename "$fullfile")
filename="${filename%.*}"

python3 start_scraper.py $fullfile >> data/$filename.start.log 2>&1 & 
echo $! > data/$filename.pid
