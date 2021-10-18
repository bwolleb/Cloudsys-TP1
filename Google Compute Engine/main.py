import os
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials

credentials = GoogleCredentials.get_application_default()
service = discovery.build('compute', 'v1', credentials=credentials)


# In order to create an external HTTP load balancer we have to pass by:
#      The default Virtual Private Cloud (VPC) network
#       A Compute Engine managed instance group
#       A named port that specifies port 80 for backend traffic
#       A default URL map
#       A backend health check
#       A frontend forwarding rule
#       A reserved external IP address


zone = 'europe-west2-a'
project = 'my-first-project-326708'  # TODO: Update placeholder value.



# this function is to create the database instance using a template
def create_instance_db(compute, project, zone, name):
    image_response = (
        compute.images()
        .getFromFamily(project="ubuntu-os-cloud", family="ubuntu-2004-lts")
        .execute()
    )
    source_disk_image = image_response["selfLink"]

    # Configure the machine
    machine_type =  "projects/my-first-project-326708/zones/%s/machineTypes/e2-small" % zone
    config = {
        "name": name,
        "machineType": machine_type,
    # Specify the boot disk and the image to use as a source.
        "disks": [
            {
                "kind": "compute#image",
                "type": "PERSISTENT",
                "boot": True,
                "mode": "READ_WRITE",
                "autoDelete": True,
                "deviceName": "instance-1",
                "initializeParams": {
                    "sourceImage": "projects/my-first-project-326708/global/images/image-db",
                    "diskType": "projects/my-first-project-326708/zones/europe-west2-a/diskTypes/pd-standard",
                    "diskSizeGb": "10",
                },
                "diskEncryptionKey": {},
            }
        ],
        "metadata": {
            "kind": "compute#metadata",
    
        },
        "networkInterfaces": [
            {
                "network":  "projects/my-first-project-326708/global/networks/default",
                "accessConfigs": [{"type": "ONE_TO_ONE_NAT", "name": "External NAT"}],
            }
        ],
        "tags": {"items": ["http-server", "https-server","mysql-3306-open"]},
    }

    return compute.instances().insert(project=project, zone=zone, body=config).execute()
# This function create a managed instance group contains 2 instances using a template for wordpress instance
def create_instance_group(compute, project):
    instance_group_manager_body = {
    
        "name": "grp_int",
        "versions": [
        {
            "name": "instance-template-wp",
            "instanceTemplate": 'https://www.googleapis.com/compute/v1/projects/my-first-project-326708/global/instanceTemplates/instance-template-wp',
            "targetSize": {
                "fixed": 2,
                "calculated": 2}
        }
        ],
        "targetSize": 2
    }
    return compute.instanceGroupManagers().insert(project=project, body=instance_group_manager_body)
# Reserving an external IP address that users use to reach load balancer
def create_External_IP_Address(compute , project):
    body ={
        "addressType": "EXTERNAL",
        "ipversion": "IPV4",
        "name": "lb-ipv4-1"
    }
    return compute.globalAddresses().insert(project=project , body= body)
# To set up the loadbalncer we have to create backend service which contain the instance group
def insert_backend_service(compute, project):
    body={
    "healthChecks": "projects/my-first-project-326708/global/healthChecks/checkhealth",
    "backends":[
        {
            "group":"projects/my-first-project-326708/zones/europe-west6-a/instanceGroups/example-managed-instance-group"

        }
    ],
    "balancingMode":"UTILIZATION",
    "protocol":"HTTP",
    "portName":"http",
    "name":"backend_service_test"
   
    }
    request = service.backendServices().insert(project=project , body=body)
    response=request.execute()
    return(response)

    
# to create the frontend for load balancer we have to create URL map
# to route the incoming requests to the default backend service
def create_url_map(compute , project , backendservice):
    return None
#Create a target HTTP proxy to route requests to URL map

def create_target_http_proxies(compute, project, url_map):
    return None
# Create a global forwarding rule to route incoming requests to the proxy

def create_forwording_rule(compute,project,ip, target_http_proxy):
    
    return None





def main():
    create_instance_db(service, project, zone, "vm-instance-db")
    response_ip = service.instances().get(project=project, zone=zone, instance="vm-instance-db").execute()
    ip_db = response_ip['networkInterfaces']['accessConfigs'][0]['natIP']
    print(ip_db)
    #create_instance_group(service, project)
    External_IP_address = create_External_IP_Address(service , project)
    ip_request = service.globalAddresses().get(project=project ,address= 'lb-ipv4-1' )
    ip_response = ip_request.execute()
    External_IP = ip_response ['address']
    print ('IP address for the load balancer: ' , External_IP )
    
    insert_backend_service(service, project) 
    # after we have to create the frontend for the loadbalancer I didn't it because it's so complicated with api 



if __name__ == "__main__":
	main()