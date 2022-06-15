# In Raspi-config ensure you have
# Set machine name, enables Wifi, disable screen-blanking and enable SSH

#git clone https://shrewdlogarithm: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@github.com/shrewdlogarithm/Gym_Cards.git

cd ~/Gym_Cards/site
bash get_tablesorter.sh
cd

sudo apt install python3-gst-1.0
pip3 install playsound

pip3 install evdev

pip3 install python_dateutil

sudo apt-get install ncftp

cd ~/Gym_Cards/system
cp -R autostart ~/.config/
cp -R lxsession/* ~/config/
cat crontab | crontab -u admin -
cd

curl https://download.argon40.com/argon1.sh | bash

sudo apt-get update
sudo apt-get upgrade
