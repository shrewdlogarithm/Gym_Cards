echo "Backup running"
date

opt=$1
if [ -z $1 ]
then
        opt=$(date +"%Y_%m_%d")
fi

cd ~/Gym_Cards

tar cvzf backups/$HOSTNAME-backup-$opt.tar.gz data/* logs/*
tar cvzf backups/$HOSTNAME-images.tar.gz site/images/*

#ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . ~/Gym_Cards/backups/*.gz

lftp -u 'gym@theedgeofthevoid.co.uk','LeeLee23"£' ftp://ftp.theedgeofthevoid.co.uk:21 <<EOF
# the next 3 lines put you in ftpes mode. Uncomment if you are having trouble connecting.
set ftp:ssl-force true
set ftp:ssl-protect-data true
set ssl:verify-certificate no
# transfer starts now...
set sftp:auto-confirm yes
mput backups/*.gz;
mirror -R -n site/images images;
exit
EOF

if [ $? -eq 0 ]
then
        rm backups/* # includes lftp status files
fi

echo "Backup Complete"
if [ $opt = "shutdown" ]
then    
        echo "Shutdown Commencing"
        sudo shutdown now
fi

