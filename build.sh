echo "1. Install CN Ubuntu Sources"
rm -rf /var/lib/dpkg/lock /var/lib/apt/lists/lock
rm -frv /var/lib/apt/lists
mkdir -pv /var/lib/lists/partial
mv /etc/apt/sources.list /etc/apt/sources.list.bak
echo '''
deb http://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ jammy-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
'''>> /etc/apt/sources.list
apt update --fix-missing && apt upgrade -y
apt-key update -y
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common -y
apt install net-tools -y
apt install python3-pip -y
pip install -U pip setuptools -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com# upgrade


echo "2. Install adb"
apt install android-tools-adb android-tools-fastboot -y


echo "3. Install sqlcipher"
apt-get install -y sqlcipher

echo "4. Update UI"
cd wechat-backup
git pull


echo "5. Install Py Library"
pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

echo "6. Install And Build silkV3"
apt-get install -y gcc g++ make ffmpeg
cd silk && make && make decoder


<<comment
apt install docker.io -y
pip3 install docker-compose -i https://mirrors.aliyun.com/pypi/simple/


mkdir /etc/docker/
echo '''{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "http://hub-mirror.c.163.com"
  ]
}''' > /etc/docker/daemon.json

systemctl daemon-reload
systemctl restart docker

docker pull greycodee/wcdb-sqlcipher
docker pull greycodee/silkv3-decoder
#docker build -t wcdb-sqlcipher:1.0 ./ -f ./wcdb-sqlcipher.dockerfile
#docker build -t silkv3-decoder:1.0 ./ -f ./silkV3-decoder.dockerfile

# install golang
apt install -y golang-go
go env -w GOPROXY=https://mirrors.aliyun.com/goproxy/,direct
go install
comment

