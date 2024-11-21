# !/bin/bash

# docker가 없다면, docker 설치
if ! type docker > /dev/null
then
  echo "docker does not exist"
  echo "Start installing docker"
  sudo apt-get update
  sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
  sudo apt update
  apt-cache policy docker-ce
  sudo apt install -y docker-ce
fi

# # docker-compose가 없다면 docker-compose 설치
# if ! type docker-compose > /dev/null
# then
#   echo "docker-compose does not exist"
#   echo "Start installing docker-compose"
#   sudo curl -L "https://github.com/docker/compose/releases/download/1.27.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
#   sudo chmod +x /usr/local/bin/docker-compose
# fi


# echo "start docker-compose up: ubuntu"
# sudo docker-compose -f /home/ubuntu/srv/ubuntu/docker-compose.yaml down

CONTAINER_NAME="minesweeper"

# 컨테이너가 존재하는지 확인
if sudo docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"
then
  sudo docker rm -f $CONTAINER_NAME
fi 

IMAGE_NAME="dojini/minesweeper:latest"

if sudo docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE_NAME}$"
then
  sudo docker rmi $IMAGE_NAME
fi

sudo docker run -it -d -p 80:8000 --name $CONTAINER_NAME $IMAGE_NAME
