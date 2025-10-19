# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

chmod 777 /var/run/docker.sock

sudo docker run hello-world


wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
rm Miniconda3-latest-Linux-x86_64.sh

conda env create -f environment.yml

conda create -n ml_faas python=3.10
conda activate ml_faas

docker pull minio/minio
mkdir -p $HOME/minio/data
docker run -d \
    -p 9000:9000 -p 9001:9001 \
    -v $HOME/minio/data:/data \
    --name "minio" \
    minio/minio:latest server /data --console-address ":9001"

sudo apt install zip unzip

unzip images.zip -d images

wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
./mc --help
sudo mv mc /usr/local/bin/mc

###
# go to ~/.mc/config.json
# add accessKey and secretKey for local
# id and password: minioadmin
###

mc cp images/* local/images
mc rm local/images/part-000001.json