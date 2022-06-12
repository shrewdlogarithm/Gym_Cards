now=$(date +"%Y_%m_%d")
tar -cvzf "backup.$now.tar,gz" ../data/* ../images/* ../logs/*
ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . "backup.$now.tar.gz"

if [ ! -f ~/Gym_Cards/active ]
then
	echo "SHUTDOWN STARTING" > ~/Gym_Cards/logs/system.log 2> &1
fi