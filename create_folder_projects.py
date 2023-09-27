# Filename: create_folder_projects.py
# Purpose: Loop through all Azure Management Groups that are children of a defined management group and create folder projects for them.
#          Note: Top-level management groups will have folder projects created prepended with Azure-

import requests
import json
import sys
import ctwiz
import logging

ARG_CLIENT_ID       = 1
ARG_CLIENT_SECRET   = 2
ARG_ROOT_MGT_GRP_ID = 3
ARG_SAML_PROVIDER   = 4
ARG_USER_ROLE       = 5
ARG_LOG_LEVEL       = 6

# Pass in runtime variables
client_id                   = sys.argv[ARG_CLIENT_ID]
client_secret               = sys.argv[ARG_CLIENT_SECRET]
root_management_group_id    = sys.argv[ARG_ROOT_MGT_GRP_ID]
default_saml_provider       = sys.argv[ARG_SAML_PROVIDER]
default_user_role           = sys.argv[ARG_USER_ROLE]
log_level                   = sys.argv[ARG_LOG_LEVEL]

def set_logging_level(level):
    match level:
        case "critical":
            logging.basicConfig(level=logging.CRITICAL)
        case "error":
            logging.basicConfig(level=logging.ERROR)
        case "warning":
            logging.basicConfig(level=logging.WARNING)
        case "debug":
            logging.basicConfig(level=logging.DEBUG)
        case "info":
            logging.basicConfig(level=logging.INFO)   
        case _:
            logging.info("Logging level not set")
            logging.basicConfig(level=logging.NOTSET)

# Uncomment the following section to define the proxies in your environment,
#   if necessary:
# http_proxy  = "http://"+user+":"+passw+"@x.x.x.x:abcd"
# https_proxy = "https://"+user+":"+passw+"@y.y.y.y:abcd"
# proxyDict = {
#     "http"  : http_proxy,
#     "https" : https_proxy
# }

users = {}

def get_role_bindings(subscription_id):

    query       = ctwiz.get_qry_role_bindings()
    variables   = ctwiz.get_qry_vars_role_bindings(subscription_id)
    results     = ctwiz.query_wiz_api(query, variables)

    # Pagination
    page_info = results["data"]["graphSearch"]["pageInfo"]

    while(page_info["hasNextPage"]):
        logging.info("Paginating on get_role_bindings")
        variables["after"] = page_info["endCursor"]
        this_results = ctwiz.query_wiz_api(query, variables)
        results["data"]["graphSearch"]["nodes"].extend(this_results["data"]["graphSearch"]["nodes"])
        page_info = this_results["data"]["graphSearch"]["pageInfo"]

    # Adding to dict to ensure duplicate results won't be added.
    role_bindings = {}

    for result in results["data"]["graphSearch"]["nodes"]:

        entities = result["entities"]

        if entities[2] != None:
            role_bindings[entities[2]["properties"]["userPrincipalName"]] = {
                "display_name" : entities[2]["properties"]["displayName"],
                "email_address"  : entities[2]["properties"]["userPrincipalName"]
            }

    return role_bindings


def model_project_structure():

    query       = ctwiz.get_qry_project_structure()
    variables   = ctwiz.get_qry_vars_project_structure(root_management_group_id)
    results     = ctwiz.query_wiz_api(query, variables)

    # Pagination
    page_info = results["data"]["graphSearch"]["pageInfo"]

    while(page_info["hasNextPage"]):
        logging.info("Paginating on model_project_structure")
        variables["after"] = page_info["endCursor"]
        this_results = ctwiz.query_wiz_api(query, variables)
        results["data"]["graphSearch"]["nodes"].extend(this_results["data"]["graphSearch"]["nodes"])
        page_info = this_results["data"]["graphSearch"]["pageInfo"]

    # Initialise structure
    structure = {}
    structure["folder_projects"] = {}
    structure["projects"]        = {}

    for result in results["data"]["graphSearch"]["nodes"]:
        entities = result["entities"]

        # Some rows returned are empty if there is no matching entity at the level of the graph, so we'll ignore these if = None.
        #entity0: tenant root group
        if entities[0] != None:
            if entities[0]["name"] not in structure["folder_projects"].keys():
                element                         = {}
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["project_id"]           = None
                element["is_folder_project"]    = True
                element["path"]                 = entities[0]["name"]
                structure["folder_projects"][entities[0]["name"]] = element

        #entity1: cloud organization - member of entity0 tenant root group

        if entities[1] != None:
            if entities[1]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"].keys():
                element                         = {}
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["project_id"]           = None
                element["is_folder_project"]    = True
                element["path"]                 = entities[0]["name"] + "/" + entities[1]["name"]
                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]] = element

        #entity2: subscription - member of entity1 cloud org
            
        if entities[2] != None:
            if entities[2]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["projects"].keys():                
                element                         = {}
                element["users"]                = get_role_bindings(entities[2]["properties"]["subscriptionExternalId"])
                element["project_id"]           = None
                element["is_folder_project"]    = False
                element["path"]                 = entities[0]["name"] + "/" + entities[1]["name"] + "/" + entities[2]["name"]

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["projects"][entities[2]["name"]] = element

        #entity3: cloud organization - member of entity1 cloud org

        if entities[3] != None:               
            if entities[3]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"].keys():
                element                         = {}
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["project_id"]           = None
                element["is_folder_project"]    = True
                element["path"]                 = entities[0]["name"] + "/" + entities[1]["name"] + "/" + entities[3]["name"]
                
                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]] = element

        #entity4: subscription - member of entity3 cloud org

        if entities[4] != None:
            if entities[4]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["projects"].keys():
                element                         = {}
                element["users"]                = get_role_bindings(entities[4]["properties"]["subscriptionExternalId"])
                element["project_id"]           = None
                element["is_folder_project"]    = False
                element["path"]                 = entities[0]["name"] + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[4]["name"]

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["projects"][entities[4]["name"]] = element
                    
        #entity5: subscription - member of tenant root management group

        if entities[5] != None:
            if entities[5]["name"] not in structure["folder_projects"][entities[0]["name"]]["projects"].keys():
                element                         = {}
                element["users"]                = get_role_bindings(entities[5]["properties"]["subscriptionExternalId"])
                element["project_id"]           = None
                element["is_folder_project"]    = False
                element["path"]                 = entities[0]["name"] + "/" + entities[5]["name"]

                structure["folder_projects"][entities[0]["name"]]["projects"][(entities[5]["name"])] = element
    
    structure["folder_projects"] = structure["folder_projects"]

    return structure

def process_folder_project(structure, parent_folder_project_id=None):

    new_structure = structure["folder_projects"]

    for l1fp in new_structure:
        
        logging.info("Creating folder project: " + new_structure[l1fp]["path"])
        new_structure[l1fp]["project_id"] = mock_create_project(l1fp, new_structure[l1fp]["path"], new_structure[l1fp]["is_folder_project"], parent_folder_project_id)
        logging.info("")

        logging.info("Processing child projects of " + l1fp + "...")
        if new_structure[l1fp]["projects"] == None:
            logging.info("- None found.")

        for project_name in new_structure[l1fp]["projects"]:
            project = new_structure[l1fp]["projects"][project_name]
            logging.info("")
            logging.info("* Creating project: " + l1fp + "/" + project_name)
            new_structure[l1fp]["projects"][project_name]["project_id"] = mock_create_project(project_name, project["path"], False, new_structure[l1fp]["project_id"])

            if len(project["users"].keys()) > 0:
                users = project["users"]
                for user_name in users:
                    mock_provision_user(users[user_name]["display_name"], users[user_name]["email_address"], default_saml_provider, default_user_role, l1fp + "/" + project_name, new_structure[l1fp]["projects"][project_name]["project_id"])
                    add_to_users_dict(users[user_name]["display_name"], users[user_name]["email_address"], default_saml_provider, default_user_role, new_structure[l1fp]["projects"][project_name]["project_id"])
                    logging.info("  - Created User: " + users[user_name]["display_name"] + "(" + users[user_name]["email_address"] + "): " + default_user_role + " on " + l1fp + "/" + project_name)

        logging.info("")
        logging.info("process_folder_project - recursing into next folder project level...")
        new_structure[l1fp]["folder_projects"] = process_folder_project(new_structure[l1fp], new_structure[l1fp]["project_id"])

    structure["folder_projects"] = new_structure

    return new_structure


# mock_create_project(project_path)
# Pretends to create a project in Wiz. Instead just writes the project path it would create to the output txt file.

def mock_create_project(project_name, full_path, is_folder = False, parent_project_id = None):
    f = open("mock_project_output.csv","a")
    project_id = project_name + "-0000-0000"

    if parent_project_id == None:
        "Project Name,Project Path,Is Folder,Project ID, Parent Project ID"
        f.write(project_name + "," + full_path + "," + str(is_folder) + "," + project_id + "," + "\n")
    else:
        f.write(project_name + "," + full_path + "," + str(is_folder) + "," + project_id + "," + parent_project_id + "\n")  

    return project_id

def add_to_users_dict(display_name, email_address, saml_provider, role, scoped_project_id):

    if email_address not in users.keys():
        user = {}
        user["display_name"] = display_name
        user["saml_provider"] = saml_provider
        user["role"] = role
        user["scoped_projects"] = set()
        user["scoped_projects"].add(scoped_project_id)
        users[email_address] = user
    else:
        users[email_address]["scoped_projects"].add(scoped_project_id)

# generate_user_import_file():
# Creates a file in a format that can be imported into Wiz using a pre-existing API recipe which is
# https://docs.wiz.io/wiz-docs/docs/api-recipes#bulk-create-pre-provision-saml-users-from-csv

def generate_user_import_file():

    f = open("user_import_file.csv","w")
    f.write("full_name,role,projects,email\n")

    for email_address in users:
        f.write(users[email_address]["display_name"] + "," + users[email_address]["role"] + "," + str(list(users[email_address]["scoped_projects"])) + "," + email_address + "\n")

# TODO
# mock_provision_user(display_name, email_address, saml_provider, role, project_path, scoped_project)
# Pretends to create a project in Wiz. Instead just writes the project path it would create to the output txt file.

def mock_provision_user(display_name, email_address, saml_provider, role, project_path, scoped_project):
    f = open("mock_user_output.csv","a")
    f.write(display_name + "," + email_address + "," + role + "," + project_path + "," + str(scoped_project) + "\n")

def initialise_mock_files():
    f = open("mock_user_output.csv","w")
    f.write("Display Name, Email Address, Role, Project Path, Scoped Project ID\n")
 
    g = open("mock_project_output.csv","w")
    g.write("Project Name,Project Path,Is Folder,Project ID, Parent Project ID\n")

def main():

    set_logging_level(log_level)

    logging.info("Getting token.")
    ctwiz.request_wiz_api_token(client_id, client_secret)

    logging.info("Initialising Mock Output Files...")
    initialise_mock_files()
    
    logging.info("Modelling project structure...")
    project_structure = model_project_structure()

    logging.info("Creating project structure...")
    process_folder_project(project_structure, None)

    logging.info("Generating user import file...")
    generate_user_import_file()

if __name__ == '__main__':
    main()