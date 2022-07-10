cd ~/Gym_Cards
dt=$(date +"%Y_%m_%d-%H:%M:%S")
tar cvzf ../preupdate$dt.gz .

git pull https://shrewdlogarithm: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@github.com/shrewdlogarithm/Gym_Cards.git

cd system
cp -R autostart ~/.config/
cp -R lxsession/* ~/.config/

cat crontab | crontab -u admin -
cd