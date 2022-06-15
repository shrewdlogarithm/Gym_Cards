echo "Scan running"
date

if [ ! -f ~/Gym_Cards/active ]
then
	bash backup.sh (date +"%H")
	sudo shutdown now
fi
