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
    * AZURE_SUBSCRIPTION_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    * AZURE_TENANT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    * AZURE_CLIENT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    * AZURE_CLIENT_SECRET = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    They can be found on the your azure portal.


## Usage
It is recommended to run the script into a python virtual environment. 
1. Log in Azure CLI by running : `az login`. 
2. Set the credentials as environment variables. For example run :
   * On Linux : `export AZURE_SUBSCRIPTION_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"`
    * On Windows : `set AZURE_SUBSCRIPTION_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"`
3. Execute the `deploy.py` file.

## Issues
In its current state, the load balancer unfortunately does not work via the script, due to an error for which no solution has been found in time. The construction of the load balancer has been disabled in the script so it still runs and créates a VM with a database and a VM with wordpress. The wordpress VM is accessible via the following IP : 20.203.160.158

