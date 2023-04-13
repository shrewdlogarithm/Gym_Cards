# In Raspi-config ensure you have
# Set machine name, enables Wifi, disable screen-blanking etc.

# Then run
# git clone https://github.com/shrewdlogarithm/Gym_Cards.git

# maybe run the following manually - just to ensure everything works as expected?

# Update everything
sudo apt-get update
sudo apt-get upgrade

# Install Tablesorter from GIT
cd ~/Gym_Cards/site
bash get_tablesorter.sh
cd

# Basic Python Requirements
pip3 install python_dateutil
pip3 install requests
pip3 install PyQuery
pip3 install flask

# For sound playback
sudo apt install python3-gst-1.0
pip3 install playsound

# For backups
sudo apt-get install lftp

# To access the cardreader (not needed/doesn't work on Windows)
pip3 install evdev
sudo usermod -a -G input $USER # may be required on some systems

# for the RFID DoorLock
pip3 install Chinese-RFID-Access-Control-Library

# For the RPi Argon Case
curl https://download.argon40.com/argon1.sh | bash

# Check for updates/install crontab/desktop shortcuts etc.
cd ~/Gym_Cards
bash system/update.sh