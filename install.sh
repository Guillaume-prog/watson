echo "Installing watson ..."

# Dependenct install
sudo apt install -y chromium-chromedriver

# Database install
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list

sudo apt update
sudo apt-get install -y mongodb
sudo systemctl enable mongod

# Install virtualenv
apt install -y python3-venv 

# Virtualenv creation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

#clear
echo "Installation complete !"
