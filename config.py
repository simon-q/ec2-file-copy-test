# Name of your auto scaling group
# Either ASG_NAME or EC2_IP_ADDRESS must be present and ASG_NAME takes precedence over EC2_IP_ADDRESS
ASG_NAME = 'simon-k-deployment-test'

# IP address of your EC2 instance
# Either ASG_NAME or EC2_IP_ADDRESS must be present and ASG_NAME takes precedence over EC2_IP_ADDRESS
EC2_IP_ADDRESS = '3.83.36.51'

# User that will be used for the SSH connection
SSH_USER = 'ec2-user'

# SSH key in OpenSSH format that will be used for the SSH connection
SSH_KEY = '/Users/simonkvasnicka/.ssh/simonk.pem'

# Root path of the directory from which all content will be put into the zip archive
# '.' will refer to a folder in which you run main.py
SOURCE = '.'

# Remote directory where the contents will be placed
# Existing files will be overwritten
TARGET = '/var/www/html/'

# Paths of files and folders that should be excluded from the content
EXCLUDES = [
    './venv',
    './.git',
    './.DS_Store'
]
