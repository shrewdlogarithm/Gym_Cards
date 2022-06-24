echo "Backup running"
date

cd ~/Gym_Cards

tar cvzf "backups/backup$1.tar.gz" data/* images/* logs/*

ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . ~/Gym_Cards/backups/*.gz
if [ $? -eq 0 ]
then
        rm backups/*.gz
fi

if [ $1 = "shutdown" ]
then
        sudo shutdown now
fi