from src import dataExtractionFunctions as extract


def generate_maas_user(user):
    """
    Generate the user resource template based on the given user information.

    Args:
        user (dict): A dictionary containing the user information.

    Returns:
        str: The formatted user resource template.

    """
    resource_template = """resource "maas_user" "{resource_name}" {{
  name = "{resource_name}"
  password = "{password}"
  email = "{email}"
  is_admin = {is_admin}
}}\n\n
"""
    return resource_template.format(
        resource_name=user["resource_name"],
        password=user["password"],
        email=user["email"],
        is_admin=user["is_admin"] if user["is_admin"] else "false",
    )


def generate_terraform_user_script(user_file):
    users = extract.csv_to_object_list(extract.read_csv_data(user_file))
    terraform_file = ""
    for user in users:
        terraform_file += generate_maas_user(user)
    return terraform_file
