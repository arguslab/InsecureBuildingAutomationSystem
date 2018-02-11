echo ================================
echo Starting Up Controller 2:
echo ================================
echo \tStarting Fan:
sudo python fan.py &
FAN_PID=$!

echo \tStarting Sensor:
sudo python sensor.py &
SENSOR_PID=$!

echo "Press enter to quit"
read useless
kill $FAN_PID
kill $SENSOR_PID
