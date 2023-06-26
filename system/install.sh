# In Raspi-config ensure you have
# Set machine name, enables Wifi, disable screen-blanking etc.

# Then run
# git clone https://github.com/shrewdlogarithm/Gym_Cards.git

# maybe run the following manually - just to ensure everything works as expected?

# Update everything
sudo apt-get update
sudo apt-get upgrade

sudo apt install git
sudo apt install python3-pip

# Install Tablesorter from GIT
cd ~/Gym_Cards/site
bash get_tablesorter.sh
cd

# For sound playback
sudo apt install python3-gst-1.0

# For backups
sudo apt-get install l

# Basic Python Requirements
pip3 install python_dateutil
pip3 install requests
pip3 install PyQuery
pip3 install flask
pip3 install playsound

# for the RFID DoorLock
pip3 install Chinese-RFID-Access-Control-Library

# To access the cardreader (pick one)
pip3 install evdev # this one for production
# pip3 install pynput # this one for Windows
sudo usermod -a -G input $USER # may be required on some systems

# for the cash drawer
sudo echo 'KERNEL=="ttyUSB0", MODE="0666"' > /etc/udev/rules.d/cashdrawer.rules
sudo usermod -a -G dialout $USER 

# to run under gunicorn
sudo apt install gunicorn
pip3 install gevent
sudo apt install gunicorn