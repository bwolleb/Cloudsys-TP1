Deploying the app wordpress + database + Loadbalancing  in GCP require :

•	One instance for database  adding firewall rule to allow mysql connection on the port 3306 and without access from the outside 
•	Group instance wich contains 2 wordpress  instances
•	Load balancer which redirect the trafic to the backend service  

Set up
•	Install the cloud SDK : 
•	Run gcloud auth application-default login 
•	Install google-api-python-client library 
•	In order to authorize requests we can use application default credentials or export env variable in which we specify the path to file.json where we have the credentials  
Requirements
 To create the instances :
•	Database image " databaseimg" based on ubunu 20.04 tls containing a preconfigured MySQL/MariaDB service with the wordpress user and wpDB table.
•	Frontend Template " instance-template-wp" based on ubuntu 20.04 tls containing a preconfigured Apache2+PHP service with the wordpress website.
In order to use Load Balancer in GCP we have to set : 
•	Backend configuration : A backend service is a group of an endpoints that receive traffic from the load balancer(External http(s) load balancer) there are several types of backends in the lab we used a managed Instance group which contains VM instances with the same set up. After creating the backend service we have to specify the protocol used by the loadbanlcer to communicate with the backend in this case http. We have also to specify the balancing mode which detemines whether bakends of a loadbalncer can handle additional traffic or are fully loaded (Rate or utilization) we used Utilization mode. 
•	Frontend configuration : Specify an IP address, port and protocol. This IP address is the frontend IP for your client's requests 
Issues :
For the script python there is no direct api to create loadbalancer . 





