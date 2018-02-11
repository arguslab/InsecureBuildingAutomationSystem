echo ================================
echo Starting Up Controller 2:
echo ================================


echo \tStarting Fan:
python fan.py &
FAN_PID=$!

echo \tStarting Sensor:
python sensor.py &
SENSOR_PID=$!

signal_handler() {
        kill -TERM $FAN_PID
        kill -TERM $SENSOR_PID
        kill -TERM $$
}
trap signal_handler INT

wait
