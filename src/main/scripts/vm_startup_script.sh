#!/usr/bin/bash

# Proxy update
gcloud compute firewall-rules create --network=covid-19-network default-allow-ssh --allow tcp:22
gcloud compute firewall-rules create --network=covid-19-network allow-debug-app --allow tcp:5000

# Setup python
sudo apt-get install -y software-properties-common python-software-properties
sudo add-apt-repository -y ppa:jonathonf/python-3.6
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -y
sudo apt-get install -y python3.6
sudo rm /usr/bin/python3
sudo ln -s /usr/bin/python3.6 /usr/bin/python3
sudo apt-get install -y python-pip python3-pip
sudo apt-get install python3.6-dev python3.6-venv
pip install --upgrade pip

# Mount GCstorage bucket
sudo apt-get install python3.6-gdbm
export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
echo "deb http://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install gcsfuse
mkdir data/
gcsfuse kaggle-covid-19-bucket data/

# Install app
git clone https://github.com/MrMimic/covid-19-applet
git clone https://github.com/MrMimic/covid-19-kaggle
cd covid-19-applet
python3 -m venv venv
source venv/bin/activate
pip install poetry
poetry install

# Download NLP stopwords and lemmatizer
python3 -m nltk.downloader stopwords
python3 -m nltk.downloader punkt

# Update local path
sed -i "s;LOCAL_DB_PATH = .*;LOCAL_DB_PATH = '/home/$USER/data/articles_database_v14_02052020_test.sqlite';" server.py
sed -i "s;LOCAL_EMBEDDING_PATH = .*;LOCAL_EMBEDDING_PATH = '/home/$USER/covid-19-kaggle/resources/global_df_w2v_tfidf.parquet';" server.py
python3 server.py