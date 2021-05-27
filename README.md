# EC2 deploy via SSH
Script that deploys contents of a source folder into a destination folder on a single EC2 instance or across all EC2 instances in an auto scaling group.
# Requirements
- Python 3 (tested with 3.8.2. 64bit on MacOS)
- AWS CLI
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html
- Init Python environment
```
python3 -m venv venv
source venv/bin/activate
```
- Install Python dependencies
```
pip install -r requirements.txt
```
# How to run
- Edit input variables in the script
  - **ec2IpAddress** or **asgName** - specify target EC2 instance or auto scaling group
  - **user** and **sshKeyFilePath** - user and SSH key needed for SSH
  - **localSourceFolder** - source folder on your local machine
  - **remoteTargetFolder** - destination folder on your EC2 instances
  - **excludes** - list of paths to exclude
- Run the script
```
python3 main.py
```
# Other links
- Using Paramiko for SSH and SCP for file transfer.
https://medium.com/@keagileageek/paramiko-how-to-ssh-and-file-transfers-with-python-75766179de73
- Paramiko
http://docs.paramiko.org/en/stable/api/client.html
- scp
https://pypi.org/project/scp/
- boto3
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html

# TODO
- config in json or yaml
