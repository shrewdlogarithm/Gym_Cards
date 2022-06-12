echo "Backup running"
date

now=$(date +"%H")

cd ~/Gym_Cards

# We don't backup the current database to avoid collisions
tar cvzf "backups/backup.$now.tar.gz" data/*.bak images/* logs/*

ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . ~/Gym_Cards/backups/*.gz
if [ $? -eq 0 ]
then
	rm backups/*.gz
fi

if [ ! -f ~/Gym_Cards/active ]
then
	echo "SHUTDOWN STARTING"
fi