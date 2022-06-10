now=$(date +"%Y_%m_%d")
tar -cvf "backup.$now.tar" data/* logs/*
#ncftpput -u gym@theedgeofthevoid.co.uk -p 'LeeLee23"£' ftp.theedgeofthevoid.co.uk . "backup.$now.tar"
