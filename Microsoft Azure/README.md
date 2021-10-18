# Microsoft Azure

## Description
The script to run is named  `deploy.py`. It will deploy instances on Microsoft Azure such as : 
* A VM with a mySQL database server
* A VM with a Wordpress website running on an Apache2 server
* A Load Balancer 

## Requirements 
To run correctly, the script needs the following requirements : 
 * Python 3.6+
 * Python "virtualenv" `pip install virtualenv`
 * Python dependencies : `pip install -r requirements.txt`
 * Set up the Azure CLI credentials : 
    * AZURE_SUBSCRIPTION_ID = ""
    * AZURE_TENANT_ID = ""
    * AZURE_CLIENT_ID = ""
    * AZURE_CLIENT_SECRET = ""

