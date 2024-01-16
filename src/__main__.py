#! /usr/bin/env python3
import argparse
from src import commands


def main():
    parser = argparse.ArgumentParser(
        prog="terramaas",
        description="Generate a network configuration Terraform file from a csv file",
        usage="%(prog)s [arguments]",
        epilog="Thanks for using Terramaas!",
    )
    subparsers = parser.add_subparsers(dest="commands")

    create_parser = subparsers.add_parser(
        "create", help="Create a network configuration Terraform file from a csv file"
    )
    create_parser.add_argument(
        "-n",
        "--network-config",
        help="The csv file containing the network configuration",
        metavar="",
        required=True,
    )
    create_parser.add_argument(
        "-p",
        "--partition-config",
        help="The csv file containing the partition configuration",
        metavar="",
        required=True,
    )
    create_parser.add_argument(
        "-u",
        "--user-config",
        help="The csv file containing the user configuration",
        metavar="",
        required=False,
    )
    create_parser.add_argument(
        "-b",
        "--node-config",
        help="The csv file containing the node configuration",
        metavar="",
        required=True,
    )
    create_parser.add_argument(
        "-i",
        "--nics-config",
        help="The csv file containing the nics configuration",
        metavar="",
        required=True,
    )
    create_parser.add_argument("--api-key", help="The MAAS API key", metavar="")
    create_parser.add_argument("--api-url", help="The MAAS API url", metavar="")
    create_parser.add_argument(
        "-a",
        "--api-config",
        help="The YAML configuration file with MAAS API key and url",
        metavar="",
    )
    create_parser.add_argument(
        "-o",
        "--output",
        help="The output file, (default: %(default)s)",
        metavar="",
        default="./terraform_script.tf",
    )
    create_parser.add_argument(
        "-y", "--yes", help="Skip the prompt to apply the changes", action="store_true"
    )

    update_parser = subparsers.add_parser(
        "update", help="Update a created MAAS network configuration"
    )
    update_parser.add_argument(
        "-d",
        "--directory",
        help="The directory containing the terraform file, (default: current directory)",
        metavar="",
        default="./",
    )

    update_parser.add_argument(
        "-n",
        "--network-config",
        help="The csv file containing the network configuration",
        metavar="",
        required=True,
    )
    update_parser.add_argument(
        "-p",
        "--partition-config",
        help="The csv file containing the partition configuration",
        metavar="",
        required=True,
    )
    update_parser.add_argument(
        "-b",
        "--node-config",
        help="The csv file containing the node configuration",
        metavar="",
        required=True,
    )
    update_parser.add_argument(
        "-i",
        "--nics-config",
        help="The csv file containing the nics configuration",
        metavar="",
        required=True,
    )
    update_parser.add_argument(
        "-u",
        "--user-config",
        help="The csv file containing the user configuration",
        metavar="",
        required=False,
    )

    update_parser.add_argument("--api-key", help="The MAAS API key", metavar="")
    update_parser.add_argument("--api-url", help="The MAAS API url", metavar="")
    update_parser.add_argument(
        "-a",
        "--api-config",
        help="The YAML configuration file with MAAS API key and url",
        metavar="",
    )
    update_parser.add_argument(
        "-o",
        "--output",
        help="The output file, (default: %(default)s)",
        metavar="",
        default="./terraform_script.tf",
    )
    update_parser.add_argument(
        "-y", "--yes", help="Skip the prompt to apply the changes", action="store_true"
    )

    destroy_parser = subparsers.add_parser(
        "destroy", help="Destroy a created MAAS network configuration"
    )
    destroy_parser.add_argument(
        "-d",
        "--directory",
        help="The directory containing the terraform file, (default: current directory)",
        metavar="",
        default="./",
    )

    args = parser.parse_args()

    if args.commands == "create":
        commands.create(args)
    elif args.commands == "update":
        commands.update(args)
    elif args.commands == "destroy":
        commands.destroy(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
