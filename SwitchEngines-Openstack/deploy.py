import os
import openstack
import yaml
import time
import base64

replaceIpScript = '''#!/bin/bash
sed -i 's/@@DATABASE-IP-PLACEHOLDER@@/{database_ip}/g' /var/www/html/wordpress/wp-config.php'''

def loadYaml(path):
	f = open(path)
	data = yaml.safe_load(f)
	f.close()
	return data

def waitInstance(client, identifier, sec=3):
	wait = True
	while wait:
		time.sleep(sec)
		instance = client.compute.find_server(identifier)
		wait = instance.status != "ACTIVE"

def findIp(instance, net):
	for a in instance.addresses[net]:
		if a["version"] == 4 and a["OS-EXT-IPS:type"] == "fixed":
			return a["addr"]
	return None

def main():
	authFile = "clouds.yaml"
	if not os.path.isfile(authFile):
		print("Please place the auth file in the same directory:", authFile)
		return

	creds = loadYaml(authFile)
	conn = openstack.connect(auth=creds["clouds"]["openstack"]["auth"])
	
	# Currently limited to 2 because of storage limit
	nbFrontends = 2
	dbImg = conn.compute.find_image("cloudsys-tp1-db-img")
	frontImg = conn.compute.find_image("cloudsys-tp1-front-img")
	flavor = conn.compute.find_flavor("n1.small")
	network = conn.network.find_network("private")
	
	# Create security groups for MySQL (tcp 3306) and HTTP(tcp 80)
	# MySQL only needs to be reachable fron the private network
	print("Creating security groups...")
	dbSecGrp = conn.network.create_security_group(name="SecGrp-DB")
	conn.network.create_security_group_rule(	security_group_id=dbSecGrp.id,
												direction="ingress",
												port_range_min=3306,
												port_range_max=3306,
												remote_ip_prefix="10.0.0.0/16",
												ether_type="IPv4",
												protocol="tcp")
	
	frontSecGrp = conn.network.create_security_group(name="SecGrp-Front")
	conn.network.create_security_group_rule(	security_group_id=frontSecGrp.id,
												direction="ingress",
												port_range_min=80,
												port_range_max=80,
												remote_ip_prefix="0.0.0.0/0",
												ether_type="IPv4",
												protocol="tcp")
	
	print("Creating database instance")
	dbInstance = conn.compute.create_server(	name="cloudsys-tp1-db",
												image_id=dbImg.id,
												flavor_id=flavor.id,
												networks=[{"uuid": network.id}],
												key_name="Main",
												security_groups=[{"name": dbSecGrp.name}])
	print("Waiting for creation of database instance...")
	waitInstance(conn, dbInstance.id)
	dbInstance = conn.compute.find_server(dbInstance.id)
	dbIp = findIp(dbInstance, network.name)
	print("Database instance has IP:", dbIp)
	
	# Process startup script with DB address
	script = replaceIpScript.format(database_ip=dbIp)
	scriptData = base64.b64encode(script.encode("utf-8")).decode("utf-8")
	frontendIps = []
	
	for i in range(1, nbFrontends + 1):
		print("Creating frontend instance", i)
		instance = conn.compute.create_server(	name="cloudsys-tp1-front" + str(i),
												image_id=frontImg.id,
												flavor_id=flavor.id,
												networks=[{"uuid": network.id}],
												key_name="Main",
												security_groups=[{"name": frontSecGrp.name}],
												user_data=scriptData)
		print("Waiting for creation of frontend instance", i, "...")
		waitInstance(conn, instance.id)
		instance = conn.compute.find_server(instance.id)
		frontIp = findIp(instance, network.name)
		frontendIps.append(frontIp)
		print("Frontend instance", i, "has IP:", frontIp)
	
	# Create loadbalancing providing the 2 hosts
	# !!! Currently not available in SwitchEngines !!!
	# Create loadbalancer
	# conn.load_balancer.create_load_balancer()
	# conn.load_balancer.create_listener()
	# conn.load_balancer.create_pool()
	# Add each frontend as member of loadbalancer pool
	# for frontend in frontendIps:
	#	conn.load_balancer.create_member()
	# Assign a new floating IP for the service
	# publicIp = conn.create_floating_ip()

if __name__ == "__main__":
	main()
