echo "Backup running"
date

cd ~/Gym_Cards

tar cvzf backups/$HOSTNAME-backup-$1.tar.gz data/* logs/*
tar cvzf backups/$HOSTNAME-images.tar.gz site/images/*

if [ -z $1 ]
then
        $1 = ""
fi

ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . ~/Gym_Cards/backups/*.gz
if [ $? -eq 0 ]
then
        rm backups/*.gz
fi

echo "Backup Complete"
if [ $1 = "shutdown" ]
then    
        echo "Shutdown Commencing"
        sudo shutdown now
fi
