# coding: utf-8
import boto3
session = boto3.Session()
ec2 = session.resource('ec2')
key_name = 'python_automation_key'
key_path = './' + key_name + '.pem'
# key = ec2.create_key_pair(KeyName=key_name)
# private_key = key.key_material
## Write the private key to a file
# with open(key_path, 'w') as key_file:
#     key_file.write(private_key)

# Change the mode of the key 
import os, stat
## Only the current user has the read and write permission to this field
os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR) 

## Get the image name to hard-code it because it doesn't change across regions
## img = ec2.Image('ami-0dc96254d5535925f')
## print(img.name)
# ami_name = 'amzn-ami-hvm-2018.03.0.20180508-x86_64-gp2'
# filters = [{'Name': 'name', 'Values': [ami_name]}]
# img = list(ec2.images.filter(Owners=['amazon'], Filters=filters))[0]

# instances = ec2.create_instances(ImageId=img.id, MinCount=1, MaxCount=1, InstanceType='t2.micro', KeyName=key.key_name)

# inst= instances[0]
# inst.wait_until_running()
# inst.reload()

# # Look up the security group
# # Authorize incoming connections from our public IP address, on port 22 (the port SSH uses)
# sg = ec2.SecurityGroup(inst.security_groups[0]['GroupId'])
# sg.authorize_ingress(IpPermissions=[{'FromPort': 22, 'ToPort': 22, 'IpProtocol': 'TCP', 'IpRanges': [{'CidrIp': '122.110.57.18/32'}]}])
# sg.authorize_ingress(IpPermissions=[{'FromPort': 80, 'ToPort': 80, 'IpProtocol': 'TCP', 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}])
