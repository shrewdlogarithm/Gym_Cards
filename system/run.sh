#gnome-terminal -- bash -c "cd ~/Gym_Cards;python3 gym.py >> logs/system.log 2>&1"
gnome-terminal -- bash -c "cd ~/Gym_Cards;gunicorn --bind 0.0.0.0:8080 --worker-class=gevent gym:app >> logs/system.log 2>&1"