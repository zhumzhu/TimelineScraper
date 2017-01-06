fullfile=$1
filename=$(basename "$fullfile")
filename="${filename%.*}"

PID=`cat data/$filename.pid`
CHILD_PID=`pgrep -P $PID`

echo "Killing main PID $PID"
kill $PID

if [ $CHILD_PID ]; then
	echo "Killing child PID $CHILD_PID"
	kill -9 $CHILD_PID
fi

rm data/$filename.pid
