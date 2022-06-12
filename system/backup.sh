now=$(date +"%Y_%m_%d")

cd ~/Gym_Cards

tar cvzf "backups/backup.$now.tar.gz" data/* images/* logs/*
ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . "~/Gym_Cards/backups/backup.$now.tar.gz"
status=$?
if [ $? -eq 0 ]; then
then
	echo "Worked"
fi

if [ ! -f ~/Gym_Cards/active ]
then
	echo "SHUTDOWN STARTING"
fi
