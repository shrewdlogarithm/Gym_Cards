# In Raspi-config ensure you have
# Set machine name, enables Wifi, disable screen-blanking etc.

# Then run
# git clone https://github.com/shrewdlogarithm/Gym_Cards.git

# maybe run the following manually - just to ensure everything works as expected?

sudo apt-get update
sudo apt-get upgrade

cd ~/Gym_Cards/site
bash get_tablesorter.sh
cd

pip3 install evdev
sudo usermod -a -G input $USER # may be required on some systems

pip3 install python_dateutil

sudo apt install python3-gst-1.0
pip3 install playsound

pip3 install Chinese-RFID-Access-Control-Library

pip3 install PyQuery

pip3 install flask

sudo apt-get install lftp

# if we're in an Argon Case
curl https://download.argon40.com/argon1.sh | bash

cd ~/Gym_Cards
bash system/update.sh