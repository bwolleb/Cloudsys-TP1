# Description
This script will deploy a working wordpress system with a database and two frontends on SwitchEngines/Openstack. It will:

- Read the auth file `clouds.yaml` (must exist in the same directory) that allows to connect to Openstack
- Create the 2 security groups, corresponding to the database and the web server profiles (more details below)
- Spawn the database instance, based on a preconfigured image
- Wait fot the instance to be active and collect its IP
- Spawn 2 instances of the frontend (see [Issues and limitations/Frontend instances](#frontend-instances) section) based on a preconfigured image, injecting the IP address of the database instance
- Collect all frontend instances IPs
- (Create a load balancer service that will split the incoming requests to all the frontends)
- (Associate afloating public IP to the load balancer)

Once finished, the service is available at http://domain/wordpress (see [Issues and limitations/Wordpress](#wordpress) section)

As the instances will receive dynamic IP addresses within the private network, the address of the database must be passed to all frontend instances to allow them to connect. The trick to inject that IP in the config is to run a small used script which will replace a placeholder string with the IP of the database that was collected when the instance was spawn.

Note: the load balancing steps are currently commented out (see [Issues and limitations/Load balancing](#load-balancing) section)

## Security groups
The following security groups will be created by the script and associated to the corresponding instances. These groups provide minimal access that allow the whole system to work.

- SecGrp-DB: Allows incoming TCP connections on port 3306 only from the private network (10.0.0.0/16). Allow all outgoing requests.
- SecGrp-Front: Allows incoming TCP connections on port 80 from anywhere. Allow all outgoing requests.

Note: the current configuration of the SecGrp-Front group allows HTTP requests from any address because these machines are intended to be exposed on the internet, but a system with a proper load balancing would only allow the HTTP requests from the load balancing service, and the load balancing service would be the only exposed interface (see [Issues and limitations/Load balancing](#load-balancing) section).

## Requirements
In order to spawn the instances, the following items must be available to the project:

- Database image "cloudsys-tp1-db-img" based on Debian 11 containing a preconfigured MySQL/MariaDB service with the wordpress user and tables
- Frontend image "cloudsys-tp1-front-img" based on Debian 11 containing a preconfigured Apache2+PHP service with the wordpress website and scripts
- a "private" network with a 10.0.0.0/16 IPv4 subnet with DHCP service

# Howto
The script is written in Python (tested with version 3.6.9) and uses the `python-openstackclient` module (installed with pip, tested with version 5.6.0).

- Place the appropriate `clouds.yaml` file in the same directory as the script
- Load the required python environment (conda, virtualenv, ...)
- Run the script: `python deploy.py`

# Issues and limitations
## Frontend instances
The account on which the system was tested currently only allows 3 running instances because of limited storage space. The total available space is 150Go and the smallest working instance consumes 20Go. The space is partially used for:

- Original database volume
- Original frontend volume
- Snapshot of database volume, dedicated to build the cloudsys-tp1-db-img image
- Snapshot of frontend volume, dedicated to build the cloudsys-tp1-db-front image

each consuming 20Go of space. So the remaining space is 70Go, allowing max 3 instances to run. This is however sufficient for a proof of concept work.

## Wordpress
The applicative service we chose is Wordpress. During the setup, Wordpress initializes all its data using the current server name, so if the service was setup using a floating IP, that same IP is saved in the database and will be used to process and serve the requests. So if the floating IP changes, Wordpress will be confused and appear broken. This is because Wordpress is intended to always run with a domain name, and updating it is not trivial

Therefore, for this lab Wordpress was setup using a fictive domain name `cloudsys-tp1` that must be used to access the service instead of using the floating public ip directly. This can be done by editing the `/etc/hosts` file for example.

This is however an issue purely related to the application and does not impact our analysis of the IaaS platforms.

## Load balancing
Although the load balancing as a service (LBaaS) seems to be actually installed on the SwitchEngines infrastructure, it is not available to our accounts and neither the GUI nor the `openstack` CLI allow to work with it. The SwitchEngines support, as discussed with M. Mendonça, have not currently processed the tickets we created about it, so the service is currently not usable.

Therefore, the deployment script does not create the load balancing service, but the steps are ready and it could be adapted as soon as LBaaS is available. This would mean:

- Adapting the frontend security group to allow incoming HTTP requests from the LBaaS only 
- Create the load balancer and add all frontends as members
- Associate a public floating IP to the load balancer
