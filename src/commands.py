# Definition of the routines associated with the subcommands
from src import generateFunctions as gf
import os
import yaml
import subprocess

TERRAFORM_PATH = '/usr/bin/terraform'

def create(args):
    
    # Get absolute paths
    csv_path = {}
    csv_path.update({"network-config": os.path.abspath(args.network_config)})
    csv_path.update({"partition-config": os.path.abspath(args.partition_config)})
    csv_path.update({"node-config": os.path.abspath(args.node_config)})
    output_path = os.path.abspath(args.output)
    
    # Get api key and url from config file or arguments
    api_key, api_url = api_config(args)
    
    # Generate Terraform script
    terraform_script = gf.generate_terraform_script(api_key, api_url, csv_path)
    
    # Write the script to a file show error if file already exists of terraform.tfstate exists
    if os.path.isfile(output_path):
        raise Exception("File already exists, please run destroy first, or use command update")
    elif os.path.isfile("terraform.tfstate"):
        raise Exception("Terraform file already exists, please run destroy first, or use command update")
    else:
        with open(output_path, "w") as f:
            f.write(terraform_script)
            
    # Apply terraform script using the command terraform apply
    subprocess.run([TERRAFORM_PATH, "init"], cwd=os.path.dirname(output_path))
    # Run terraform plan to preview changes
    subprocess.run([TERRAFORM_PATH, "plan"], cwd=os.path.dirname(output_path))
    
    # Prompt the user to continue or abort
    if args.yes:
        subprocess.run([TERRAFORM_PATH, "apply", "-auto-approve"], cwd=os.path.dirname(output_path))
    else:
        user_input = input("Do you want to apply the changes? (yes/no): ")
        if user_input.lower() == "yes":
            subprocess.run([TERRAFORM_PATH, "apply", "-auto-approve"], cwd=os.path.dirname(output_path))
        else:
            print("Aborted.")
        
        
# Update the network configuration if terraform exists in current directory
def update(args):
    
    # Get absolute paths
    csv_path = os.path.abspath(args.csv)
    output_path = os.path.abspath(args.output)
    
    # Get api key and url from config file or arguments
    api_key, api_url = api_config(args)
    
    # Generate Terraform script
    terraform_script = gf.generate_terraform_script(api_key, api_url, csv_path)
    if os.path.isfile("terraform.tfstate"):
        subprocess.run([TERRAFORM_PATH, "plan"], cwd=os.path.dirname(args.directory))
        # Prompt the user to continue or abort
        if args.yes:
            subprocess.run([TERRAFORM_PATH, "apply", "-auto-approve"], cwd=os.path.dirname(args.directory))
        else:
            user_input = input("Do you want to apply the changes? (yes/no): ")
            if user_input.lower() == "yes":
                subprocess.run([TERRAFORM_PATH, "apply", "-auto-approve"], cwd=os.path.dirname(args.directory))
            else:
                print("Aborted.")
    else:
        raise Exception("No terraform file found")        
    
    
# call terraform destroy to destroy the network configuration if terraform exists in current directory    
def destroy(args):
    if os.path.isfile("terraform.tfstate"):
        subprocess.run([TERRAFORM_PATH, "destroy"], cwd=os.path.dirname(args.directory))
    else:
        raise Exception("No terraform file found")
    

# Function to handle api configuration
def api_config(args):
    # Check if api key and url are provided or in a config file
    if args.api_key is None or args.api_url is None:
        if args.api_config is None:
            raise Exception("Either api key and url must be provided or a config file")
        
    # Get api key and url from config file or arguments
    if args.api_config:
        try:
            with open(os.path.abspath(args.api_config)) as f:
                config = yaml.load(f, Loader=yaml.SafeLoader)
                api_key = config['api_key']
                api_url = config['api_url']
        except:
            raise Exception("Error reading config file")
    else:
        api_key = args.api_key
        api_url = args.api_url
        
    return api_key, api_url
