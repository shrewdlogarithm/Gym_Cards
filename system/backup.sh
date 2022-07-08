echo "Backup running"
date

now=$(date +"\%Y_\%m_\%d_\%H")

cd ~/Gym_Cards

tar cvzf backups/$HOSTNAME-backup-$now.tar.gz data/* site/images/* logs/*

ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . ~/Gym_Cards/backups/*.gz
if [ $? -eq 0 ]
then
        rm backups/*.gz
fi

if [ $1 = "shutdown" ]
then
        sudo shutdown now
fi