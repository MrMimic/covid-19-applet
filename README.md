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
- Ubuntu 16.04
- Startup script:
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
        # Run app
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
