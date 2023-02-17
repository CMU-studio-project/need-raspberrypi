# need-raspberrypi
raspberrypi repository for NEED Project

## Installation
We recommend virtual environment (i.e. venv/conda) for installation. We tested on virtualenv.
```shell
pip install -r app/requirements.txt
```

#### .env file
To add informations of ip address and device information, copy `.env.template` file and change the name into `.env` and fill it.

#### Credentials
To use Google Pub/Sub, you need service account key with corresponding privilege. \\
For more information, see [Google Service Account Documentation](https://cloud.google.com/iam/docs/service-accounts)
```
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service/account/key.json
```
or you can write it on `.env` file


#### Run app 
```shell
cd app/
python main.py
```
