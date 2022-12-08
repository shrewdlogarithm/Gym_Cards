echo "Backup running"
date

curl https://api.dynu.com/nic/update?hostname=gymlee.mywire.org&password=leelee23

host=$HOSTNAME
opt=$1
if [ -z $1 ]
then
        opt=$(date +"%Y_%m_%d")
fi

cd ~/Gym_Cards

tar czf backups/${host}-backup-$opt.tar.gz data/* logs/*

#ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . ~/Gym_Cards/backups/*.gz

lftp -u 'gym@theedgeofthevoid.co.uk','LeeLee23"£' ftp://ftp.theedgeofthevoid.co.uk:21 -e "set ftp:ssl-force true;set ftp:ssl-protect-data true;set ssl:verify-certificate no;set sftp:auto-confirm yes;mput backups/*.gz;mirror -R -n site/images ${host}images;exit"

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

