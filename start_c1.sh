echo ================================
echo Starting Up Controller 1:
echo ================================
echo \tStarting Alarm:
python alarm.py &
ALARM_PID=$!

echo \tStarting Web:
python web.py &
WEB_PID=$!

echo \tStarting TC:
python temp_control.py &
TC_PID=$!

signal_handler() {
        kill -TERM $ALARM_PID
        kill -TERM $TC_PID
        kill -TERM $WEB_PID
        kill -TERM $$
}
trap signal_handler INT

wait
