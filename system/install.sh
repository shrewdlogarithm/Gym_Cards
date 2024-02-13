# IMPORTANT NOTE: If you're not me - the main problem here is gym.py - that contains some comments which might help you see how this works

sudo apt install git

# To install from scratch
git clone https://github.com/shrewdlogarithm/Gym_Cards.git

# IMPORTANT -  I would run the following manually as there are decisions I was too lazy to code as questions!

# Update everything
sudo apt-get update
sudo apt-get upgrade

sudo apt install python3-pip

# For sound playback
sudo apt install python3-gst-1.0

# For backups
sudo apt install lftp

# Basic Python Requirements
pip3 install python_dateutil
pip3 install requests
pip3 install PyQuery
pip3 install flask
pip3 install playsound

# IMPORTANT - below here are mostly Linux OR Windows choices so this is where you need a bit of manual effort - sorry again!

# for the RFID DoorLock (Linux only)
pip3 install Chinese-RFID-Access-Control-Library

# To access the cardreader (choose)
pip3 install evdev # this one for Linux
pip3 install pynput # this one for Windows - HAS PERFORMANCE PROBLEMS ON LINUX
sudo usermod -a -G input $USER 

# for the cash drawer (Linux only)
sudo echo 'KERNEL=="ttyUSB0", MODE="0666"' > /etc/udev/rules.d/cashdrawer.rules
sudo usermod -a -G dialout $USER 

# production WSGI server (Linux only)
sudo apt install gunicorn
pip3 install gevent

# Lastly - if you're restoring the entire system this pulls the last image from the cloud backup
cd ~/Gym_Cards/system
sh restore.sh