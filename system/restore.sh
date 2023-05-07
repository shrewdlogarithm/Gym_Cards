host=$1
if [ -z $1 ]
then
    echo "Requires HOSTNAME as parameter"
else
    cd ~/Gym_Cards
    lftp -u 'gym@theedgeofthevoid.co.uk','LeeLee23"£' ftp://ftp.theedgeofthevoid.co.uk:21 -e "set ftp:ssl-force true;set ftp:ssl-protect-data true;set ssl:verify-certificate no;set sftp:auto-confirm yes;mirror -n ${host}images site/images;mirror -n ${host}logs logs ;mirror -n ${host}data data ;exit"
fi