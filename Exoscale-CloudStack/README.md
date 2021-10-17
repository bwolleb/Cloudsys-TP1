# About

The `main.py` script creates and wire together the following services on Exoscale:

- Two security groups
  - The database security group only allows connection on the MySQL port 3306 from members of the web server security group (no access from outside).
  - The webserver security group allows access on the port 80 from the outside.
- One instance pool with 2 machines (web servers)
- One database instance
- One load balancer, redirecting queries to all instances of the instance pool

The `create-templates.sh` script is a helper script that creates templates from snapshots.

# Requirements

1. First we need to create templates for the webserver and the database
    1. Setup MySQL server: https://docs.rackspace.com/support/how-to/install-mysql-server-on-the-ubuntu-operating-system/
    2. Setup Apache and PHP (skip MySQL!): https://www.digitalocean.com/community/tutorials/how-to-install-linux-apache-mysql-php-lamp-stack-ubuntu-18-04
    3. Setup wordpress: https://wordpress.org/support/article/how-to-install-wordpress/
    4. Shutdown the instances and create snapshots from the website
    5. Install exoscale cli https://community.exoscale.com/documentation/tools/exoscale-command-line-interface/ 
    6. Setup exoscale cli: `exo config`
    7. Run `./create-templates.sh` and pass the two snapshots id. The first ID must be the webserver and the second one the database
2. Install python (at least version 3.6)
   1. Setup a `venv` if you don't want to polute your global installation
   2. Run `pip install -r requirements.txt`
3. Patch compute.py
   1. There is a bug in exoscale that makes it impossible to set a security group without a private network (which we didn't need for this exercice)
   2. A PR as been submitted to their repo but may not be in yet. If you get a `TypeError: 'NoneType' object is not iterable` please replace `instance_security_groups` by `instance_private_networks` in the file that errors.  (There are better way to do this but they would take a bit of time)
   3. Another bug prevents doing http check without setting up `tsl-sni`, if the API returns "the healthcheck field is incorrect", remove `"tls-sni": healthcheck_tls_sni,` in the file that errors.

# Usage

1. First you need to set env variables with the API key and secret: `export EXOSCALE_API_KEY="EXOxxxxxxxxxxxxxxxxx" EXOSCALE_API_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxx"` (they can be obtained on the website)
2. Run the `main.py` script and pass the templates UUIDs e.g: `python main.py --db-template 8cf659ac-fd8d-475c-86da-f96189a84ce9 --web-template f7892431-5ada-4f86-b91b-b65a5cc4d87d`

Additional args:
```
  --clean true                 Delete everything that can be deleted. Database instance still needs to be deleted manually
  --db-template DB_TEMPLATE    DB Template ID
  --web-template WEB_TEMPLATE  Webserver Template ID
  --no-db true                 Skip database creation, need to specify database IP
  --db-ip DB_IP                IP of the database if skip DB is set
```

# Known issues

- Wordpress stores its domain in the database and in other places and was designed with using a domain name in mind, this script runs a command to fix it but sometimes it does not work and if the IP changes it needs to be ran again. Since a real solution would use a DNS, this problem has not been fixed completely.
- The `--clean` does not clean the database instance and security groups cannot be deleted while they are in use, so the database must be deleted manually for it to work.