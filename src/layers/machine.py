from src import dataExtractionFunctions as extract
import re


def csv_to_object_list(data):
    headers = [header.lower().strip().replace(" ", "_") for header in data[0]]
    obj_list = []
    for row in data[1:]:
        row = [r.strip() for r in row]
        row = ",".join(row)
        comma_outside_quotes = re.compile(r",(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)")
        row = comma_outside_quotes.split(row)
        obj = dict(zip(headers, row))
        for key, value in obj.items():
            obj[key] = value.replace('"', "")
        obj_list.append(obj)
    return obj_list


def generate_terraform_resource_machine(data):
    """
    Generates a Terraform resource block for a machine.

    Args:
        data (dict): A dictionary containing the data for the resource block.
            - "resource_name" (str): The name of the resource.
            - "power_type" (str): The type of power for the machine.
            - "power_pass" (str): The password for the power.
            - "power_address" (str): The address for the power.
            - "pxe_mac_address" (str): The PXE MAC address for the machine.

    Returns:
        str: The generated Terraform resource block for the machine.
    """
    resource_template = """resource "maas_machine" "{resource_name}" {{
    power_type = "{power_type}"
    power_parameters = {{
        power_pass = "{power_pass}"
        power_address = "{power_address}"
    }}
    pxe_mac_address = "{pxe_mac_address}"
    }}\n\n"""

    resource_block = resource_template.format(
        resource_name=data["resource_name"],
        power_type=data["power_type"],
        power_pass=data["power_pass"],
        power_address=data["power_address"],
        pxe_mac_address=data["pxe_mac_address"],
    )
    return resource_block


def generate_partition(partition):
    """
    Generate the partition resource template based on the given partition information.

    Args:
        partition (dict): A dictionary containing the partition information.

    Returns:
        str: The formatted partition resource template.

    """
    resource_template = """partitions {{
     size_gigabytes = "{size_gigabytes}"
     fs_type        = "{fs_type}"
     label          = "{label}"
     bootable       = "{bootable}"
     mount_point    = "{mount_point}"
    }}\n\n
    """
    return resource_template.format(
        size_gigabytes=partition["size_gigabytes"],
        fs_type=partition["fs_type"],
        label=partition["label"],
        bootable=partition["bootable"],
        mount_point=partition["resource_name"],
    )


def generate_nic(machine_name, data):
    """
    Generates a resource template for a physical network interface.

    Parameters:
        data (dict): A dictionary containing the following keys:
            - nic_name (str): The name of the network interface.
            - mac_address (str): The MAC address of the network interface.
            - resource_name (str): The name of the resource.
            - vlan_id (number): The vlan id associated.
            - tags (Set of String): A set of tag names to be assigned to the physical network interface

    Returns:
        str: The generated resource template.
    """
    ip_address = ""
    if data["ip_address"] and data["mode"].toupper() == "STATIC":
        ip_address = f'ip_address = "{data["ip_address"]}"'
    tags = ""
    if data["tags"] != "None":
        tags = '","'.join(("tag1,tag2,tag3".split(",")))
        tags = f'tags = ["{tags}"]'

    resource_template = """resource "maas_network_interface_physical" "{resource_name}-{nic_name}"{{
        machine     = maas_machine.{resource_name}.id
        mac_address = "{mac_address}"
        name        = "{nic_name}"
        vlan        = maas_vlan.vlan-{vlan_id}.vid
        {tags}
}}\n\n

resource "maas_network_interface_link" "{resource_name}-{nic_name}" {{
  machine = maas_machine.{resource_name}.id
  network_interface = maas_network_interface_physical.{resource_name}-{nic_name}.id
  mode = "{mode}"
  {ip_address}
  default_gateway = {default_gateway}
  subnet = maas_subnet.{subnet}.id
}}
    """
    return resource_template.format(
        nic_name=data["resource_name"],
        mac_address=data["mac_address"],
        resource_name=machine_name,
        vlan_id=data["vlan_id"],
        tags=tags,
        mode=data["mode"].upper(),
        ip_address=ip_address,
        default_gateway=data["default_gateway"] or False,
        subnet=data["subnet_name"],
    )


def generate_block_device(data, partition_csv):
    """
    Generates a block device resource template based on the provided data and partition CSV.

    :param data: A dictionary containing the data for generating the resource template.
    :type data: dict
    :param partition_csv: A list of dictionaries representing the partition CSV.
    :type partition_csv: list
    :return: The generated resource template as a string.
    :rtype: str
    """
    resource_template = """resource "maas_block_device" "{resource_name}" {{
  machine = maas_machine.{resource_name}.id
  name = "{name}"
  id_path = "{id_path}"
  size_gigabytes = "{size}"
  {partitions}
}}\n\n
"""
    partitions = ""
    total_size = 0
    for p in partition_csv:
        partitions += generate_partition(p)
        total_size += int(p["size_gigabytes"])
    return resource_template.format(
        resource_name=data["resource_name"],
        name=data["resource_name"],
        id_path=data["id_path"],
        size=total_size,
        partitions=partitions,
    )


def generate_terraform_node_script(machines_config, partitions_config, nics_config):
    """
    Generates a Terraform script for creating resources based on the provided machines and partitions configurations.

    :param machines_config: The path to the machines configuration CSV file.
    :type machines_config: str
    :param partitions_config: The path to the partitions configuration CSV file.
    :type partitions_config: str
    :return: The generated Terraform script as a string.
    :rtype: str
    """
    terraform_file = ""

    machines = csv_to_object_list(extract.read_csv_data(machines_config))
    partitions = csv_to_object_list(extract.read_csv_data(partitions_config))
    nics = csv_to_object_list(extract.read_csv_data(nics_config))
    for machine in machines:
        terraform_file += generate_terraform_resource_machine(machine)
        terraform_file += generate_block_device(
            machine,
            [
                part
                for part in partitions
                if part["resource_name"] in machine["partition_schema"].split(",")
            ],
        )
        for nic in nics:
            if nic["resource_name"] in [
                nic.strip() for nic in machine["nic_name"].split(",")
            ]:
                terraform_file += generate_nic(machine["resource_name"], nic)
    return terraform_file
