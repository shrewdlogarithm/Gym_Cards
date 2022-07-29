cd ~/Gym_Cards
dt=$(date +"%Y_%m_%d-%H:%M:%S")
tar cvzf ../preupdate$dt.gz .

git pull https://github.com/shrewdlogarithm/Gym_Cards.git

cd system
cp -R autostart ~/.config/
cp -R lxsession/* ~/.config/

cat crontab | crontab -u admin -
cd