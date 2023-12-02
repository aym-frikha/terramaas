from src.layers import network as net
from src.layers import machine as node

# PROVIDER BLOCK
def generate_terraform_provider(provider_name, provider_attributes):
    # Define the basic template for the provider block
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
    # Define the basic template for the resource block
    resource_template = """resource "{resource_type}" "{resource_name}" {{
{attributes}
}}\n\n"""

    # Format the attributes
    formatted_attributes = "\n".join(f'  {key} = "{value}"' for key, value in resource_attributes.items())

    # Combine the template and attributes to create the resource block
    resource_block = resource_template.format(resource_type=resource_type, resource_name=resource_name,
                                              attributes=formatted_attributes)

    return resource_block



# Generate complete terraform script
def generate_terraform_script(api_key, api_url, csv_files):
    terraform_script = """terraform {
      required_providers {
        maas = {
          source  = "maas/maas"
          version = "~>1.0"
        }
      }
    }\n\n"""

    # Add provider block
    terraform_script += generate_terraform_provider("maas",
                                                    {"api_version": "2.0", "api_key": api_key, "api_url": api_url})

    terraform_script += net.generate_terraform_network_script(csv_files['network-config'])
    terraform_script += node.generate_terraform_node_script(csv_files['node-config'], csv_files['partition-config'])

    return terraform_script
