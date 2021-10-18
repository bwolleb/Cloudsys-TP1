from typing import Protocol
from azure.identity import AzureCliCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
import os
import resources

credential = AzureCliCredential()

subscription_id = os.environ['AZURE_SUBSCRIPTION_ID'] 

resource_client = ResourceManagementClient(credential, subscription_id)

# Resource group
RESOURCE_GROUP_NAME = "labo1-rg"
LOCATION = "switzerlandnorth"
USERNAME = "azureuser"
PASSWORD = "Azureuser123"

# Network
VNET_NAME = 'myVNet'
SUBNET_NAME = 'MyBackendSubnet'

PUBLIC_IP_NAME = 'myPublicIP'

#Load Balancer
LB_NAME = 'myLoadBalancer'
FIP_NAME = 'LoadBalancerFrontend'
ADDRESS_POOL_NAME = 'myBackendPool'

PROBE_NAME = 'myHealthProbe'
LB_RULE_NAME = 'myHTTPRule'
NETRULE_NAME_1 = 'myNSGRule'
NETRULE_NAME_2 = 'Port_3306'


# MYSQL VM IMAGE
MYSQL_IMAGE_NAME = "mySQL-VM-Image"
MYSQL_NETWORK_INTERFACE_ID = resources.MYSQL_NETWORK_INTERFACE_ID

# WORDPRESS : VM with Wordpress on it
WORDPRESS_IMAGE_NAME = "wordpress-VM-image"
WORDPRESS_NETWORK_INTERFACE_NAME = 'myVM1-wordpress-nsg'

# Obtain the management object for virtual machines
compute_client = ComputeManagementClient(credential, subscription_id)

# Network client
network_client = NetworkManagementClient(credential, subscription_id)

# LoadBalancer Frontend Instance
def create_lb():
    print(f'Creating Load Balancer')

    load_balancing_rules = [{
        'name' : LB_RULE_NAME,
        'protocol' : 'tcp',
        'frontend_port' : 80,
        'backend_port' : 80,
        'idle_timeout_in_minutes' : 15,
        'enable_floating_ip' : False,
        'load_distribution' : 'Default',
        'frontend_ip_configuration' : {
            "id": "/subscriptions/f1ad079d-efe5-45de-accd-9988e201e5c3/resourceGroups/labo1-rg/providers/Microsoft.Network/loadBalancers/myLoadBalancer/frontendIPConfigurations/LoadBalancerFrontend",
        },
        'backend_address_pool' : {
            "id": "/subscriptions/f1ad079d-efe5-45de-accd-9988e201e5c3/resourceGroups/labo1-rg/providers/Microsoft.Network/loadBalancers/myLoadBalancer/backendAddressPools/myBackendPool",
        },
        'probe' : {
            "id": "/subscriptions/f1ad079d-efe5-45de-accd-9988e201e5c3/resourceGroups/labo1-rg/providers/Microsoft.Network/loadBalancers/myLoadBalancer/probes/myHealthProbe",
        }
    }]

    poller = network_client.load_balancers.begin_create_or_update(
        RESOURCE_GROUP_NAME,
        LB_NAME,
        {
            # 'id' : LB_ID,
            'location' : LOCATION,
            'frontend_ip_configuration' : {
                'name' : PUBLIC_IP_NAME,
                'id' : resources.PUBLIC_IP_ID,
            },
            'backend_address_pool' : [
                {
                    'name' : 'myBackendPool',
                    'id' : resources.ADDRESS_POOL_ID
                }
            ],
            'probes' : [
                {
                    'name' : 'myHealthProbe',
                    'id' : resources.HEALTH_PROBE_ID,
                }
            ],
            'load_balancing_rules' : [
                {
                    'name' : 'myHTTPRule',
                    "id": resources.LB_RULE_ID,
                }
            ],
            'sku' : {
                'name' : 'Standard',
            }
        }
    )
    lb_result = poller.result()
    print(lb_result)

# DB VM
def create_database_vm():
    print(f'Creating Database VM')
    poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, MYSQL_IMAGE_NAME,
        {
            "location": LOCATION,
            "storage_profile": {
                "image_reference": {
                    "id" : resources.MYSQL_IMAGE_ID,
                }
            },
            "hardware_profile": {
                "vm_size": "Standard_DS1_v2"
            },
            "os_profile": {
                "computer_name": MYSQL_IMAGE_NAME,
                "admin_username": USERNAME,
                "admin_password" : PASSWORD,
            },
            "network_profile": {
                "network_interfaces": [{
                    "id": MYSQL_NETWORK_INTERFACE_ID,
                }]
            }        
        }
    )

    vm_result = poller.result()
    print(vm_result)

def create_wordpress_vm():
    print(f'Creating Wordpress VM')
    poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, WORDPRESS_IMAGE_NAME,
        {
            "location": LOCATION,
            "storage_profile": {
                "image_reference": {
                    "id" : resources.WORDPRESS_IMAGE_ID,
                }
            },
            "hardware_profile": {
                "vm_size": "Standard_DS1_v2"
            },
            "os_profile": {
                "computer_name": WORDPRESS_IMAGE_NAME,
                "admin_username": USERNAME,
                "admin_password" : PASSWORD,
            },
            "network_profile": {
                "network_interfaces": [{
                    "id": resources.WORDPRESS_NETWORK_INTERFACE_ID,
                }]
            }        
        }
    )

    vm_result = poller.result()
    print(vm_result)

def run_deploy():
    create_lb()
    create_wordpress_vm()
    create_database_vm()

if __name__ == "__main__":
    run_deploy()
    print(f'opération completed')