sudo apt-get update
sudo apt install -y python3-pip
pip3 install -r ../requirements

wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
tar -xzf geckodriver-v0.24.0-linux64.tar.gz
mv geckodriver /usr/local/bin/

git clone https://github.com/MattEding/Instruments.git
