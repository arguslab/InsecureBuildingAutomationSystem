echo ================================
echo Starting Up Controller 1:
echo ================================
echo \tStarting Web:
python web.py &
WEB_PID=$!

echo \tStarting TC:
python temp_control.py &
TC_PID=$!

echo "Press enter to quit"
read useless
kill $WEB_PID
kill $TC_PID
