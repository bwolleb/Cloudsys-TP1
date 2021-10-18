# AWS
Before the beggining of the deployement, you need to install the librairie in the "requirement.txt"
You need to connect with your AWS account.
The following instruction can be use to connect to your AWS account :
1) you need to create a user key in IAM service
2) get Acces Key and Secret Acces Key
3) Execute in the console : aws configure
3.1) Enter Acces Key
3.2) Enter Secret Access Key
3.3) Enter Region : us-west-2
3.4) Enter extension : json

# Generate Key Pair
The python file generatekeypair.py file can create a key pair to connect to aws (key-pair.ppm).

# Deployement
The python file deploy.py can create a new VM instance with a ubuntu distribution. The instance do nothing for the moment.
