import csv

CIDR_COLUMN = "CIDR"
GATEWAY_COLUMN = "Gateway"
MTU_COLUMN = "MTU"
DYNAMIC_RANGE_COLUMN = "Dynamic Range"
RESERVED_RANGE_COLUMN = "Reserved Range"
VLAN_COLUMN = "VLAN"
FABRIC_COLUMN = "Fabric"


# Function to extract data from a csv file
def read_csv_data(csv_file):
    data = []
    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
            
    return data


# extract network data from a csv file
def extract_network_data(data):
    # Identify the start of the data
    skip_rows = 0
    for row in data:
        if row[1] == "CIDR":
            break
        skip_rows += 1
            
    return data[skip_rows+1:]



# Extract columns names and associated index from csv data
def extract_column_names(data):
    columns = {}
    for row in data:
        if row[1] == "CIDR":
            for index, column in enumerate(row):
                columns[column] = index
            break
    return columns


#Extract space name from the extracted data
def extract_space_name(space_name_cell):
    # Change spaces to dashes
    space_name = space_name_cell.replace(" ", "-")
    space_name = space_name + "-space"
    return space_name
    

# Extract space info from the extracted data
def extract_spaces_list(data):
    spaces = []
    data = extract_network_data(data)
    # Create a list of dictionaries to store the space data
    for line in data:
        if line[0] != "":
            spaces.append(extract_space_name(line[0]))
            
    return list(set(spaces))


# Extract fabric info from the extracted data
def extract_fabric_list(data):
    fabrics = []
    columns = extract_column_names(data)
    data = extract_network_data(data)
    # Create a list of dictionaries to store the fabric data
    for line in data:
        if line[columns[FABRIC_COLUMN]] != "":
            fabrics.append(line[columns[FABRIC_COLUMN]])
            
    return list(set(fabrics))


# Extract vlan info from the extracted data
def extract_vlan_list(data):
    vlans = []
    columns = extract_column_names(data)
    data = extract_network_data(data)
    # Create a list of dictionaries to store the vlan data
    for row in data:
        vlan_cell = row[columns[VLAN_COLUMN]]
        if is_valid_vlan(vlan_cell):           
            vlan = {
                "vlan_id": vlan_cell,
                "vlan_name": "vlan-" + vlan_cell,
                "space_name": extract_space_name(row[0]),
                "fabric_name": row[columns[FABRIC_COLUMN]],
                "mtu" : row[columns[MTU_COLUMN]]
            }
            vlans.append(vlan)
        
    return list({vlan['vlan_id']: vlan for vlan in vlans}.values())


# Extract subnet info from the extracted data
def extract_subnets_list(data):
    # Create a list of dictionaries to store the subnet data
    subnets = []
    columns = extract_column_names(data)
    for subnet in data:
        # Skip rows with empty fields 
        if not all(field.strip() == '' for field in subnet[1:]) and is_valid_vlan(subnet[columns[VLAN_COLUMN]]):
            subnet_name = subnet[0].replace(" ", "-")
            attributes = {
                "cidr": subnet[columns[CIDR_COLUMN]],
                "gateway_ip": subnet[columns[GATEWAY_COLUMN]],
            }
            
            # Create a list of dictionaries to store the ip ranges
            ip_ranges = []
            dynamic_range = subnet[columns[DYNAMIC_RANGE_COLUMN]]
            # Append the dynamic range to the ip range list
            ip_ranges.extend(extract_ip_ranges(dynamic_range, "dynamic"))
                    
            # Append the reserved range to the ip range list
            reserved_range = subnet[columns[RESERVED_RANGE_COLUMN]]
            ip_ranges.extend(extract_ip_ranges(reserved_range, "reserved"))
                    
            subnets.append({
                "subnet_name": subnet_name,
                "fabric_name": subnet[columns[FABRIC_COLUMN]],
                "attributes": attributes,
                "ip_ranges": ip_ranges,
                "vlan_name": "vlan-" + subnet[columns[VLAN_COLUMN]],
            })     
            
    return subnets


# Extract ip ranges from the extracted data
def extract_ip_ranges(ip_range_cell, ip_range_type):
    # Create a list of dictionaries to store the ip ranges
    ip_ranges = []
    if ip_range_cell:
        ip_range_list = ip_range_cell.split(";")
        for ip_range in ip_range_list:
            ip_range = extract_ip_range(ip_range, ip_range_type)
            ip_ranges.append(ip_range)
            
    return ip_ranges

# Extract ip range into dictionary
def extract_ip_range(ip_range, ip_range_type):
    ip_range = ip_range.split("-")
    if len(ip_range) == 2:
        start_ip , end_ip = ip_range
        return {
            "type": ip_range_type,
            "start_ip": start_ip,
            "end_ip": end_ip
        }
    else:
        return None


# Validate th vlan value
def is_valid_vlan(vlan_value):
    try:
        vlan_int = int(vlan_value)
        return 0 <= vlan_int <= 4094
    except ValueError:
        return False