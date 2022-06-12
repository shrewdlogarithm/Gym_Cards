echo "Startup running"
date

echo "On" > ~/Gym_Cards/active

now=$(date +"%Y_%m_%d_%H")

cd ~/Gym_Cards

# We don't backup the current database to avoid collisions
tar cvzf "backups/backup.$now.tar.gz" data/*.bak images/* logs/*