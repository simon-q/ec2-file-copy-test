# EC2 deploy via SSH
Using Paramiko for SSH and SCP for file transfer.
https://medium.com/@keagileageek/paramiko-how-to-ssh-and-file-transfers-with-python-75766179de73

# Requirements
- Python 3 (tested with 3.8.2. 64bit on MacOS)
- AWS CLI
- boto3
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
- Paramiko
http://docs.paramiko.org/en/stable/api/client.html
- scp
https://pypi.org/project/scp/

# Init
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# How to run
Edit input variables in the script and run it
```
python3 main.py
```
