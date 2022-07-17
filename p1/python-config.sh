echo "Upgrade the system"

sudo apt update && sudo apt upgrade -y

echo "Install the build toolchain"
sudo apt install build-essential -y
echo "Install Python3"
sudo apt install python3 python3-dev python3-pip -y 


pip install -r p1/requirement.txt

cd p1

export FLASK_APP=app
flask run