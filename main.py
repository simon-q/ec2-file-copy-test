import io
import os
import sys
import zipfile
import boto3
import paramiko
import scp
import config
import uuid

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
    if config.EXCLUDES:
        for excludedPath in config.EXCLUDES:
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
    if sent == size:
        sys.stdout.write('done     \r')
    else:
        sys.stdout.write(" %.2f%%\r" % (float(sent)/float(size)*100))

# @param host: str
def deploy(host):
    # Establish SSH connection
    sshKey = paramiko.RSAKey.from_private_key_file(config.SSH_KEY)
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    sshClient.connect(
        hostname=host,
        username=config.SSH_USER,
        pkey=sshKey
    )

    # Zip all contents in the specified path except for excluded paths
    zipFile = getZipFileForDir(config.SOURCE)
    # Upload zip file to home directory, by default this would be /home/ec2-user/
    with scp.SCPClient(sshClient.get_transport(), progress=progress) as scpClient:
        scpClient.putfo(zipFile, 'deployment.zip')
    zipFile.close()
    
    # Unzip contents into a temp folder
    tempFolderName = f'temp-{uuid.uuid1()}'
    sshClient.exec_command(f'unzip -u deployment.zip -d {tempFolderName}')
    # Copy contents from temp folder to website root folder
    sshClient.exec_command(f'sudo cp -a {tempFolderName}/. {config.TARGET}')
    # Remove temp folder
    sshClient.exec_command(f'sudo rm -rf {tempFolderName}')
    # Remove zip file
    sshClient.exec_command('sudo rm -rf deployment.zip')

    sshClient.close()

def main():
    ipAddresses = []
    if config.ASG_NAME:
        ipAddresses = getIpAddressesForInstancesInAsg(config.ASG_NAME)
    else:
        ipAddresses = [config.EC2_IP_ADDRESS]
    
    print('Starting deployment to these IP addresses:')
    print(ipAddresses)
    print('---')

    for ipAddress in ipAddresses:
        print(f'Deploying to: {ipAddress}')
        
        deploy(ipAddress)
        
        print('done')
        print('---')

main()
