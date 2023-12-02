from src import dataExtractionFunctions as extract

def csv_to_object_list(data):
    obj_list = []
    part = {}
    for header in data[0]:
        part.update({header: ""})
    for row in data[1:]:
        for header, value in zip(data[0], row):
            part[header] = value
        obj_list.append(part)
    return obj_list


def generate_terraform_resource_machine(data):

    resource_template = """resource "maas_machine" "{resource_name}" {{
    power_type = "{power_type}"
    power_parameters = {{
        power_pass = "{power_pass}"
        power_address = "{power_address}"
    }}
    pxe_mac_address = "{pxe_mac_address}"
    }}\n\n"""

    resource_block = resource_template.format(
        resource_name=data["Resource Name"],
        power_type=data["power_type"],
        power_pass=data["power_pass"],
        power_address=data["power_address"],
        pxe_mac_address=data["pxe_mac_address"])
    return resource_block


def generate_partition(partition):
    resource_template = """partitions {{
     size_gigabytes = "{size_gigabytes}"
     fs_type        = "{fs_type}"
     label          = "{label}"
     bootable       = "{bootable}"
     mount_point    = "{mount_point}"
    }}\n\n
    """
    return resource_template.format(
        size_gigabytes=partition['size_gigabytes'],
        fs_type=partition['fs_type'],
        label=partition['label'],
        bootable=partition['bootable'],
        mount_point=partition['mount_point']
    )


def generate_nic(data):
    resource_template = """resource "maas_network_interface_physical" {nic_name}{{
        machine     = maas_machine.{resource_name}.id
        mac_address = "{mac_address}"
        name        = "{nic_name}"
    }}\n\n
    """
    return resource_template.format(
        nic_name=data['nic_name'],
        mac_address=data['mac_address'],
        resource_name=data['Resource Name']
    )


def generate_block_device(data, partition_csv):
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
        total_size += int(p['size_gigabytes'])
    return resource_template.format(
        resource_name=data['Resource Name'],
        name=data['Resource Name'],
        id_path=data['id_path'],
        size=total_size,
        partitions=partitions
    )


def generate_terraform_node_script(machines_config, partitions_config):
    terraform_file = ""
    machines = csv_to_object_list(extract.read_csv_data(machines_config))
    partitions = csv_to_object_list(extract.read_csv_data(partitions_config))
    for machine in machines:
        terraform_file += generate_terraform_resource_machine(machine)
        terraform_file += generate_block_device(machine,
                                                [part for part in partitions
                                                 if part['Resource Name'] in machine["partition_schema"].split(",")])
        terraform_file += generate_nic(machine)
    return terraform_file
