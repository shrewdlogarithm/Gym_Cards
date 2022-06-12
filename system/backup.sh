now=$(date +"%Y_%m_%d")

cd ~/Gym_Cards
pwd

tar -cvzf "backups/backup.$now.tar,gz" data/* images/* logs/*
ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . "backups/backup.$now.tar.gz"

if [ ! -f ~/Gym_Cards/active ]
then
	echo "SHUTDOWN STARTING" > ~/Gym_Cards/logs/system.log 2>&1
fi
