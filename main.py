import io
import os
import sys
import zipfile
import boto3
import paramiko
import scp

########
# inputs
# change these to match your environment

# Name of your auto scaling group
# Either asgName or ec2IpAddress must be present and asgName takes precedence over ec2IpAddress
asgName = 'simon-k-deployment-test'

# IP address of your instance
# Either asgName or ec2IpAddress must be present and asgName takes precedence over ec2IpAddress
ec2IpAddress = '3.83.36.51'

# User that will be used for the SSH connection
user = 'ec2-user'

# SSH key in OpenSSH format that will be used for the SSH connection
sshKeyFilePath = '/Users/simonkvasnicka/.ssh/simonk.pem'

# Root path of the directory from which all content will be put into the zip archive
contentPath = '.'

# Paths of files and folders that should be excluded from the content
excludes = [
    './venv',
    './.git',
    './.DS_Store'
]

# Remote directory where the contents will be placed
# Existing files will be overwritten
remoteTargetFolder = '/var/www/html/'

#########
# scripts

# @param asgName: str
# @return str[]
def getIpAddressesForInstancesInAsg(asgName):
    ipAddresses = []
    if asgName:
        # Get auto scaling group
        client = boto3.client('autoscaling')
        response = client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[asgName]
        )
        asgs = response.get('AutoScalingGroups')
        if not asgs: return
        asg = asgs[0]
        if not asg: return

        # Get ec2 instances in the auto scaling group
        instances = asg.get('Instances')
        if not instances: return
        instanceIds = []
        for instance in instances:
            instanceIds.append(instance['InstanceId'])

        # Get public IP address for each ec2 instance
        client = boto3.client('ec2')
        response = client.describe_instances(
            InstanceIds=instanceIds
        )
        reservations = response.get('Reservations')
        if not reservations: return
        for reservation in reservations:
            instances = reservation.get('Instances')
            if not instances: continue
            for instance in instances:
                ipAddresses.append(instance['PublicIpAddress'])
    return ipAddresses

# @param path: str
# @return BytesIO
def getZipFileForDir(path):
    inMemoryZip = io.BytesIO()

    with zipfile.ZipFile(inMemoryZip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        addDirToZip(path, zf)

    inMemoryZip.seek(0)
    return inMemoryZip

# @param path: str
# @return bool
def isExcluded(path):
    for excludedPath in excludes:
        if path.startswith(excludedPath):
            return True
    return False

# @param path: str
# @param ziph: ZipFile
def addDirToZip(path, ziph):
    for root, dirs, files in os.walk(path):
        if isExcluded(root):
            break
        for file in files:
            ziph.write(
                os.path.join(root, file), 
                os.path.relpath(
                    os.path.join(root, file),
                    os.path.join(path, '.')
                )
            )

# @param filename: str
# @param size: float
# @param sent: float
def progress(filename, size, sent):
    sys.stdout.write("%s's progress: %.2f%%   \r" % (filename, float(sent)/float(size)*100))

# @param host: str
def deploy(host):
    # Establish SSH connection
    sshKey = paramiko.RSAKey.from_private_key_file(sshKeyFilePath)
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.connect(
        hostname=host,
        username=user,
        pkey=sshKey
    )

    # Zip all contents in the specified path except for excluded paths
    zipFile = getZipFileForDir(contentPath)
    # Upload zip file to home directory, by default this would be /home/ec2-user/
    with scp.SCPClient(sshClient.get_transport(), progress=progress) as scpClient:
        scpClient.putfo(zipFile, 'deployment.zip')
    zipFile.close()
    
    # Unzip contents into a temp folder
    sshClient.exec_command('unzip -u deployment.zip -d temp')
    # Copy contents from temp folder to website root folder
    sshClient.exec_command(f'sudo cp -a temp/. {remoteTargetFolder}')
    # Remove temp folder
    sshClient.exec_command('sudo rm -rf temp')
    # Remove zip file
    sshClient.exec_command('sudo rm -rf deployment.zip')

    sshClient.close()

def main():
    ipAddresses = []
    if asgName:
        ipAddresses = getIpAddressesForInstancesInAsg(asgName)
    else:
        ipAddresses = [ec2IpAddress]
    
    print('Starting deployment to these IP addresses:')
    print(ipAddresses)
    print('---')

    for ipAddress in ipAddresses:
        print(f'Deploying to: {ipAddress}')
        
        deploy(ipAddress)
        
        print('done')
        print('---')

main()
