# covid-19-applet


### Installation

#### Create folder

    mkdir c19_project
    cd c19_project

#### Clone applet repository

    git clone https://github.com/MrMimic/covid-19-applet

#### Check Python'v version

    python3 --version

Should be >= 3.6.1. Update if needed.

#### Create venv

    python3 -m venv venv
    source venv/bin/activate

#### Download Kaggle dataset

Use the kaggle API:

    pip install kaggle
    kaggle datasets download allen-institute-for-ai/CORD-19-research-challenge

#### Create the local database

Clone the lib repository:

    git clone https://github.com/MrMimic/covid-19-kaggle

Install the developped kaggle lib:

    pip install -q git+https://github.com/MrMimic/covid-19-kaggle

Make modifications in the script: covid-19-kaggle/src/main/scripts/create_db.py

- L:17      local_path="articles_database.sqlite"
- L:18      kaggle_data_path="kaggle_data"

Should be changed by your local paths to wanted DB file and downloaded dataset.

At the moment, let run_on_kaggle and only_covid params to True, otherwise the resulting DB will weight 22Go instead of 700Mo.

Run the database creation:

    python3 covid-19-kaggle/src/main/scripts/create_db.py

#### Install web applet

    pip install poetry
    poetry install

#### Run applet

Make change to __server.py__. It needs the DB you just created and the path to the pre-trained word2vec coming with the repository of the lib code:

- L15:        LOCAL_DB_PATH = "<path_to_trained_db>"
- L16:        LOCAL_EMBEDDING_PATH = "<path_to_cloned_library>/covid-19-kaggle/resources/global_df_w2v_tfidf.parquet"

Then run server:

    python3 server.py

Go to http://<hostname>:5000.

Watch out, data are stored in cache for only 10min right now. First time you launch the server and a new query after 10 min of inactivity will last ~30sec.

#### Troubleshot

- Open port if distant host

#### GCP

##### VM

- E2
- Debian9
- Startup script:

    #! /bin/bash
    # Update
    apt-get -y update
    apt-get -y upgrade
    # Update python
    apt-get install build-essential
    curl -O https://www.python.org/ftp/python/3.6.8/Python-3.6.8.tar.xz
    tar -xf Python-3.6.8.tar.xz
    cd Python-3.6.8
    ./configure --enable-optimizations
    make -j 8
    sudo make altinstall
    cd /usr/bin
    sudo rm python3
    sudo ln -s /usr/local/bin/python3.6 python3
    apt-get install -y python-pip
    apt-get install -y python3-pip
    # Linking bucket
    mkdir /bucket
    gcsfuse kaggle-covid-19-bucket /bucket