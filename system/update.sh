cd
dt=$(date +"%Y_%m_%d")
tar cvzf preupdate$dt.gz Gym_Cards/.*
cd Gym_Cards
git pull https://shrewdlogarithm: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@github.com/shrewdlogarithm/Gym_Cards.git

cd system
cp -R autostart ~/.config/
cp -R lxsession/* ~/.config/

cat crontab | crontab -u admin -
cd