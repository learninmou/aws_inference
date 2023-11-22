set -ex

timedatectl set-timezone Asia/Shanghai

apt update
apt install -y python3-pip
#apt install -y awscli
#aws configure
pip3 install sagemaker
pip3 install boto3 uvicorn fastapi httpx gunicorn
