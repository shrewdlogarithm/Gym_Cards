echo "Startup running"
date

echo "On" > ~/Gym_Cards/active

now=$(date +"%Y_%m_%d_%H")

cd ~/Gym_Cards

tar cvzf "backups/backup.$now.tar.gz" data/*.bak images/* logs/*
# at some point we should purge logs here?