# Description: This file contains all the functions used to generate the terraform files
from src import dataExtractionFunctions as extract

# PROVIDER BLOCK
def generate_terraform_provider(provider_name, provider_attributes):
    #Define the basic template for the provider block
    provider_template = """provider "{provider_name}" {{ 
{attributes}    
}}\n\n"""
    
    # Format the attributes
    formatted_attributes = "\n".join(f'  {key} = "{value}"' for key, value in provider_attributes.items())
    
    # Combine the template and attributes to create the provider block
    provider_block = provider_template.format(provider_name=provider_name, attributes=formatted_attributes)
    
    return provider_block



# RESOURCE BLOCKS
def generate_terraform_resource(resource_type, resource_name, resource_attributes):
    #Define the basic template for the resource block
    resource_template = """resource "{resource_type}" "{resource_name}" {{
{attributes}
}}\n\n"""

    # Format the attributes
    formatted_attributes = "\n".join(f'  {key} = "{value}"' for key, value in resource_attributes.items())
    
    # Combine the template and attributes to create the resource block
    resource_block = resource_template.format(resource_type=resource_type, resource_name=resource_name, attributes=formatted_attributes)
    
    return resource_block


# FABRIC RESOURCE BLOCK
def generate_terraform_resource_fabric(fabric_name):
    return generate_terraform_resource("maas_fabric", fabric_name, {"name": fabric_name})
    


# SPACE RESOURCE BLOCK
def generate_terraform_resource_space(space_name):
    return generate_terraform_resource("maas_space", space_name, {"name": space_name})
    

# VLAN RESOURCE BLOCK
def generate_terraform_resource_vlan(vlan_resource_name, vid, fabric_name, space_name, mtu=1500):
    #Define the basic template for the resource block
    resource_template = """resource "maas_vlan" "{resource_name}" {{
  fabric = maas_fabric.{fabric_name}.id
  space = maas_space.{space_name}.id
  vid = {vid}
  name = "{resource_name}"
  mtu = {mtu}
}}\n\n"""  


    # Combine the template and attributes to create the resource block
    resource_block = resource_template.format(resource_name=vlan_resource_name, vid=vid, fabric_name=fabric_name, space_name=space_name, mtu=mtu)
    
    return resource_block


# SUBNET RESOURCE BLOCK
def generate_terraform_resource_subnet(subnet_resource_name, subnet_resource_attributes, subnet_ip_ranges, subnet_dns_servers, fabric_name, vlan_name):
    #Define the basic template for the resource block
    resource_template = """resource "maas_subnet" "{resource_name}" {{
  fabric = maas_fabric.{fabric_name}.id
  vlan = maas_vlan.{vlan_name}.vid
{attributes}
{dns_servers}{ip_ranges}
}}\n\n
"""
    # Format the attributes
    formatted_attributes = "\n".join(f'  {key} = "{value}"' for key, value in subnet_resource_attributes.items())
    
    # Format dns_servers if array is not empty
    if subnet_dns_servers:
        formatted_dns_servers_list = "\n".join(f'   "{value}",' for value in subnet_dns_servers)
        formatted_dns_servers = f'  dns_servers = [\n{formatted_dns_servers_list}\n  ]\n'
    else:
        formatted_dns_servers = ""

    
    # Format the ip ranges
    formatted_ip_ranges = "\n".join(generate_ip_range(ip_range["type"], ip_range["start_ip"], ip_range["end_ip"]) for ip_range in subnet_ip_ranges)
     
    # Combine the template and attributes to create the resource block
    resource_block = resource_template.format( 
        resource_name=subnet_resource_name,
        fabric_name=fabric_name, 
        vlan_name=vlan_name,  
        attributes=formatted_attributes,
        dns_servers=formatted_dns_servers, 
        ip_ranges=formatted_ip_ranges)
    
    return resource_block
    
def generate_ip_range(ip_range_type, start_ip, end_ip):
    #Define the basic template for the resource block
    ip_range_template = """  ip_ranges {{
    type = "{ip_range_type}"
    start_ip = "{start_ip}"
    end_ip = "{end_ip}"
  }}"""
    
    # Combine the template and attributes to create the resource block
    ip_range_block = ip_range_template.format(ip_range_type=ip_range_type, start_ip=start_ip, end_ip=end_ip)
    
    return ip_range_block


# Generate complete terraform script
def generate_terraform_script(api_key, api_url, csv_file):
    terraform_script = """terraform {
  required_providers {
    maas = {
      source  = "maas/maas"
      version = "~>1.0"
    }
  }
}\n\n"""


    # Add provider block
    terraform_script += generate_terraform_provider("maas", {"api_version": "2.0" ,"api_key": api_key, "api_url": api_url})
    
    # Extract data from csv file
    data = extract.read_csv_data(csv_file)
    
    # Add fabric blocks
    fabric_list = extract.extract_fabric_list(data)
    for fabric in fabric_list:
        if fabric == "default" or fabric == "fabric-1":
            continue
        terraform_script += generate_terraform_resource_fabric(fabric)
        
    # Add space blocks
    space_list = extract.extract_spaces_list(data)
    for space in space_list:
        terraform_script += generate_terraform_resource_space(space)
        
    # Add vlan blocks
    vlan_list = extract.extract_vlan_list(data)
    for vlan in vlan_list:
        terraform_script += generate_terraform_resource_vlan(vlan["vlan_name"], vlan["vlan_id"], vlan["fabric_name"], vlan["space_name"], vlan["mtu"]   )
        
    # Add subnet blocks
    subnet_list = extract.extract_subnets_list(data)
    for subnet in subnet_list:
        terraform_script += generate_terraform_resource_subnet(subnet["subnet_name"], subnet["attributes"], subnet["ip_ranges"], "", subnet["fabric_name"], subnet["vlan_name"])
        
    return terraform_script