now=$(date +"%Y_%m_%d")
tar -cvf "backup.$now.tar" data/* logs/*
#ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . "backup.$now.tar"

if [ ! -f ~/Gym_Cards/active ]
then
	echo "SHUTDOWN STARTING" > ~/Gym_Cards/logs/system.log 2> &1
fi