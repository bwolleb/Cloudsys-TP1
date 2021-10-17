import exoscale
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage wordpress and database on exoscale')
    parser.add_argument('--clean', default=False, type=bool, nargs='+', help='Destroy all instances, security groups and more!')
    parser.add_argument('--db-template', required=True, type=str, nargs=1, help='DB Template ID')
    parser.add_argument('--web-template', required=True, type=str, nargs=1, help='Webserver Template ID')
    parser.add_argument('--no-db', type=bool, nargs=1, default=False, help='Skip database creation')
    parser.add_argument('--db-ip', type=str, nargs=1, default=False, help='IP of the database if skip DB is set')

    args = parser.parse_args()

    if args.no_db and not args.db_ip:
        print("If --no-db is specified, --db-ip must be passed as it is required to setup webserver")
        exit()

    exo = exoscale.Exoscale()
    zone = exo.compute.get_zone("ch-dk-2")

    template_webserver = None
    template_db = None
    security_group_web = None
    security_group_database = None

    try:
        template_webserver = exo.compute.get_instance_template(zone, id=args.web_template[0])
        template_db = exo.compute.get_instance_template(zone, id=args.db_template[0])
    except Exception as e:
        print(e)
        print("Could not find templates!")

    # Check existing security groups and retrieve them if they exists
    for security_group in exo.compute.list_security_groups():
        if security_group.name == "wordpress-automated":
            security_group_web = security_group
        if security_group.name == "database-automated":
            security_group_database = security_group

    if args.clean:
        print("Deleting load balancer")
        try:
            load_balancer = exo.compute.get_network_load_balancer(zone, name="webserver-load-balancer-automated")
            load_balancer.delete()
        except:
            print("Could not delete load balancer")

        print("Deleting webserver instance pool")
        try:
            webserver_instance_pool = exo.compute.get_instance_pool(zone, name="webserver-pool-automated")
            webserver_instance_pool.delete()
        except:
            print("Could not delete webserver instance pool")

        print("Deleting security groups")
        try:
            security_group_database.delete()
        except:
            print("Could not delete database security group")
        try:
            security_group_web.delete()
        except:
            print("Could not delete web security group")

        print("Database instance still has to be deleted manually from the website!")

        exit()

    # Create security groups if they don't exists
    print("Creating security groups")
    if security_group_web is None:
        security_group_web = exo.compute.create_security_group("wordpress-automated")
        security_group_web.add_rule(
            exoscale.api.compute.SecurityGroupRule.ingress(
                description="HTTP",
                network_cidr="0.0.0.0/0",
                port="80",
                protocol="tcp",
            )
        )
        print("Created security group 'webserver-automated'")
    else:
        print("Security group webserver-automated already exist, skipping creation")

    if security_group_database is None:
        security_group_database = exo.compute.create_security_group("database-automated")
        security_group_database.add_rule(
            exoscale.api.compute.SecurityGroupRule.ingress(
                description="MySQL",
                security_group=security_group_web,
                port="3306",
                protocol="tcp",
            )
        )
        print("Created security group 'database-automated'")
    else:
        print("Security group database-automated already exist, skipping creation")

    load_balancer = None
    try:
        load_balancer = exo.compute.get_network_load_balancer(zone, name="webserver-load-balancer-automated")
    except:
        print("Creating load balancer")

    if load_balancer is None:
        load_balancer = exo.compute.create_network_load_balancer(zone, "webserver-load-balancer-automated")
        print("Created load balancer")
    else:
        print("Using existing load balancer")

    instance_db_server = None
    if not args.no_db:
        print("Creating mysql-server from template")
        instance_db_server = exo.compute.create_instance(
            name="mysql-server-automated",
            zone=zone,
            type=exo.compute.get_instance_type("micro"),
            template=template_db,
            volume_size=10,
            security_groups=[security_group_database],
            user_data="# config db")

        print("Created database")
    else:
        print("Skipped Database instance creation")

    db_ip = None
    if instance_db_server is None:
        db_ip = args.db_ip
    else:
        db_ip = instance_db_server.ipv4_address

    web_user_data = f"""#!/bin/sh
runcmd:
    - sudo sed -i 's/159.100.246.153/{db_ip}/g' /var/www/html/wp-config.php
    - sudo curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
    - php wp-cli.phar --path='/var/www/html/' search-replace '159.100.253.18' '{load_balancer.ip_address}'
"""

    webserver_instance_pool = None
    try:
        webserver_instance_pool = exo.compute.get_instance_pool(zone, name="webserver-pool-automated")
    except:
        print("Creating instance pool")

    if webserver_instance_pool is None:
        webserver_instance_pool = exo.compute.create_instance_pool(
            name="webserver-pool-automated",
            zone=zone,
            size=2,  # Number of instances managed by this pool
            instance_type=exo.compute.get_instance_type("micro"),
            instance_template=template_webserver,
            instance_volume_size=10,
            instance_security_groups=[security_group_web],
            instance_user_data=web_user_data)
        print(f"Created instance pool")
    else:
        print("Using existing instance pool")

    service_exists = False
    for service in load_balancer.services:
        if service.name == "webserver-service-automated":
            service_exists = True
            print("Service already exists in load balancer")
            break

    if not service_exists:
        print("Adding service to load balancer")
        load_balancer.add_service("webserver-service-automated", 
            webserver_instance_pool, 80, 120, target_port=80,
            healthcheck_retries=1, healthcheck_timeout=5, healthcheck_mode="http",
            healthcheck_uri="/license.txt", healthcheck_tls_sni="")

    print(f"Website should be accessible soon on http://{load_balancer.ip_address}")
