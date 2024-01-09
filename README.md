# Terramaas

Automated Terraform deployment for MAAS.

---

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
    - [Creating Network Configurations](#creating-network-configurations)
    - [Updating Network Configurations](#updating-network-configurations)
    - [Destroying Network Configurations](#destroying-network-configurations)

## Introduction

Terramaas is a Python-based tool designed to simplify and automate the deployment of network resources in a MAAS (Metal as a Service) environment using Terraform. This project provides an easy-to-use solution for generating Terraform scripts, streamlining the setup and configuration of your network infrastructure within a MAAS environment. 

## Installation

Terramaas can be installed using snap:

```bash
sudo snap install terramaas --classic
```
 
## Usage

Terramaas provides a CLI with various commands:

`create` : Generate network configuration Terraform files from CSV files.

`update` : Update MAAS network configurations.

`destroy` : Destroy MAAS network configurations.

### Creating Network Configurations

To create a network configuration Terraform file from a CSV, use the `create` command. You'll need to specify the CSV file containing the network configuration and the MAAS API configuration file (or provide API key and URL). For example:

```bash
terramaas create --node-config node_config.csv --partition-config partition_config.csv --network-config network_config.csv --api-config key.yaml
```

#### Options:
| Option | Description | Default | Required |
| --- | --- | --- | --- |
| `--csv`, `-c` | CSV file containing network configuration | | Yes |
| `--api-config`, `-a` | MAAS API configuration file | | Yes* |
| `--api-key` | MAAS API key | | Yes* |
| `--api-url` | MAAS API URL | | Yes* |
| `--output`, `-o` | Output file name | ./terraform_script.tf | No |

*Either `api-config` or `api-key` and `api-url` are required.

#### CSV Example:

| | CIDR | Gateway | MTU | Dynamic Range | Reserved Range | VLAN | Fabric |
| --- | --- | --- | --- | --- | --- | --- | --- |  
| Openstack Public API | 10.20.0.0/24 | 10.20.0.1 | 1500 | 10.20.0.10-10.20.0.100 | 10.20.0.101-10.20.0.200 | 412 | fab-2 |

#### API Configuration File:

```yaml
---
api_key: <MAAS_API_KEY>
api_url: <MAAS_API_URL>
```

### Updating Network Configurations

To update a network configuration in MAAS, use the `update` command. You'll need to specify the updated CSV File describing the network configuration, the API configuration file (or provide API key and URL), and the output file name. For example:

```bash
terramaas update --node-config node_config.csv --partition-config partition_config.csv --network-config network_config.csv --api-config key.yaml
```

#### Options:
| Option, Shorthand | Description | Default | Required |
| --- | --- | --- | --- |
| `--csv`, `-c` | CSV file containing network configuration | | Yes |
| `--api-config`, `-a` | MAAS API configuration file | | Yes* |
| `--api-key` | MAAS API key | | Yes* |
| `--api-url` | MAAS API URL | | Yes* |
| `--output`, `-o` | Output file name | ./terraform_script.tf | No |
| `--directory`, `-d` | Directory containing Terraform state files | ./ | No |
| `--yes`, `-y` | Skip confirmation prompt | False | No |

*Either `api-config` or `api-key` and `api-url` are required.


### Destroying Network Configurations

To destroy a network configuration in MAAS, use the `destroy` command.

```bash
terramaas destroy -d <tfstate_directory>
```

#### Options:
| Option, Shorthand | Description | Default | Required |
| --- | --- | --- | --- |
| `--directory`, `-d` | Directory containing Terraform state files | ./ | No |



