# Filename: create_folder_projects.py
# Purpose: Loop through all Azure Management Groups that are children of a defined management group and create folder projects for them.
#          Note: Top-level management groups will have folder projects created prepended with Azure-

import requests
import json
import sys
import ctwiz
import logging

ARG_CLIENT_ID               = 1
ARG_CLIENT_SECRET           = 2
ARG_AZURE_ROOT_MG_LIST      = 3
ARG_SAML_PROVIDER           = 4
ARG_USER_ROLE               = 5
ARG_LOG_LEVEL               = 6
ARG_WIZ_DATACENTER          = 7
ARG_GCP_ROOT_ORG_LIST       = 8
ARG_AWS_ROOT_ORG_LIST       = 9


# Pass in runtime variables
client_id                           = sys.argv[ARG_CLIENT_ID]
client_secret                       = sys.argv[ARG_CLIENT_SECRET]
azure_root_management_group_list    = sys.argv[ARG_AZURE_ROOT_MG_LIST]
default_saml_provider               = sys.argv[ARG_SAML_PROVIDER]
default_user_role                   = sys.argv[ARG_USER_ROLE]
log_level                           = sys.argv[ARG_LOG_LEVEL]
wiz_datacenter                      = sys.argv[ARG_WIZ_DATACENTER]
gcp_root_org_list                   = sys.argv[ARG_GCP_ROOT_ORG_LIST]
aws_root_org_list                   = sys.argv[ARG_AWS_ROOT_ORG_LIST]

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
root_structure = {}

root_structure["AWS"]                       = {}
root_structure["AWS"]["folder_projects"]    = {}
root_structure["AWS"]["projects"]           = {}
root_structure["AWS"]["is_folder_project"]  = True
root_structure["AWS"]["project_id"]         = None
root_structure["AWS"]["path"]               = "AWS/"

root_structure["Azure"] = {}
root_structure["Azure"]["folder_projects"]      = {}
root_structure["Azure"]["projects"]             = {}
root_structure["Azure"]["is_folder_project"]    = True
root_structure["Azure"]["project_id"]           = None
root_structure["Azure"]["path"]                 = "Azure/"

root_structure["GCP"]                       = {}
root_structure["GCP"]["folder_projects"]    = {}
root_structure["GCP"]["projects"]           = {}
root_structure["GCP"]["is_folder_project"]  = True
root_structure["GCP"]["project_id"]         = None
root_structure["GCP"]["path"]               = "GCP/"

root_burner_structure = {}

root_burner_structure["AWS"] = {}
root_burner_structure["AWS"]["folder_projects"] = {}
root_burner_structure["AWS"]["projects"]        = {}
root_burner_structure["AWS"]["is_folder_project"] = True

root_burner_structure["Azure"] = {}
root_burner_structure["Azure"]["folder_projects"] = {}
root_burner_structure["Azure"]["projects"]        = {}
root_burner_structure["Azure"]["is_folder_project"] = True

root_burner_structure["GCP"]   = {}
root_burner_structure["GCP"]["folder_projects"] = {}
root_burner_structure["GCP"]["projects"]        = {}
root_burner_structure["GCP"]["is_folder_project"] = True



def get_role_bindings(subscription_id, cloud):

    query       = ctwiz.get_qry_role_bindings()
    variables   = ctwiz.get_qry_vars_role_bindings(subscription_id, cloud)
    results     = ctwiz.query_wiz_api(query, variables, wiz_datacenter)

    # Pagination
    page_info = results["data"]["graphSearch"]["pageInfo"]

    while(page_info["hasNextPage"]):
        logging.info("Paginating on get_role_bindings")
        variables["after"] = page_info["endCursor"]
        this_results = ctwiz.query_wiz_api(query, variables, wiz_datacenter)
        results["data"]["graphSearch"]["nodes"].extend(this_results["data"]["graphSearch"]["nodes"])
        page_info = this_results["data"]["graphSearch"]["pageInfo"]

    # Adding to dict to ensure duplicate results won't be added.
    role_bindings = {}

    for result in results["data"]["graphSearch"]["nodes"]:

        entities = result["entities"]

        if entities[2] != None and cloud == "Azure":
            role_bindings[entities[2]["properties"]["userPrincipalName"]] = {
                "display_name" : entities[2]["properties"]["displayName"],
                "email_address"  : entities[2]["properties"]["userPrincipalName"]
            }

        if entities[2] != None and cloud == "GCP":
            role_bindings[entities[2]["properties"]["name"]] = {
                "display_name" : entities[2]["properties"]["name"],
                "email_address"  : entities[2]["properties"]["name"]
            }

        if entities[2] != None and cloud == "AWS":
            role_bindings[entities[2]["properties"]["name"]] = {
                "display_name" : entities[2]["properties"]["name"],
                "email_address"  : entities[2]["properties"]["name"]
            }


    return role_bindings

def model_project_structure(burner_mode, root_mg_id, cloud, mg_friendly_name, mg_burner_list):

    logging.info("Cloud: " + cloud + " - Burner Mode: " + str(burner_mode) + " - Root Mgmt Group: " + root_mg_id)
    query       = ctwiz.get_qry_project_structure()
    variables   = {}

    if burner_mode      == True and cloud == "Azure":
        variables   = ctwiz.get_qry_vars_azure_project_structure_burners(root_mg_id, mg_burner_list[0])
    elif burner_mode    == False and cloud == "Azure":
         variables  = ctwiz.get_qry_vars_azure_project_structure_excl_burners(root_mg_id, mg_burner_list[0])  
    elif burner_mode    == True and cloud == "GCP":
        variables   = ctwiz.get_qry_vars_gcp_project_structure_burners(root_mg_id, mg_burner_list[0])
    elif burner_mode    == False and cloud == "GCP":
        variables   = ctwiz.get_qry_vars_gcp_project_structure_excl_burners(root_mg_id, mg_burner_list[0])
    elif burner_mode    == True and cloud == "AWS":
        logging.info("No burner mode for AWS")
        return None
    elif burner_mode    == False and cloud == "AWS":
        variables   = ctwiz.get_qry_vars_aws_project_structure(root_mg_id)  
    
    results     = ctwiz.query_wiz_api(query, variables, wiz_datacenter)

    # Pagination
    page_info = results["data"]["graphSearch"]["pageInfo"]

    while(page_info["hasNextPage"]):
        logging.info("Paginating on model_project_structure")
        variables["after"] = page_info["endCursor"]
        this_results = ctwiz.query_wiz_api(query, variables, wiz_datacenter)
        results["data"]["graphSearch"]["nodes"].extend(this_results["data"]["graphSearch"]["nodes"])
        page_info = this_results["data"]["graphSearch"]["pageInfo"]

    logging.info("Exited Pagination")

    # Initialise structure

    structure = {}
    structure["folder_projects"]    = {}
    structure["projects"]           = {}
    structure["is_folder_project"]  = True
    structure["path"]               = cloud + "/" + mg_friendly_name

    logging.info(str(len(results["data"]["graphSearch"]["nodes"])) + " Results fetched")
    i = 0

    for result in results["data"]["graphSearch"]["nodes"]:
        i = i + 1
        
        logging.info("Processing result " + str(i) + " of " + str(len(results["data"]["graphSearch"]["nodes"])))
        
        entities = result["entities"]

        # Some rows returned are empty if there is no matching entity at the level of the graph, so we'll ignore these if = None.
        #entity0: tenant root group

        if entities[0] != None:
            if entities[0]["name"] not in structure["folder_projects"].keys():
                element                         = {}
                element["external_id"]          = entities[0]["properties"]["externalId"]
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["project_id"]           = None
                element["is_folder_project"]    = True
                element["path"]                 = cloud + "/" + entities[0]["name"]
                structure["folder_projects"][entities[0]["name"]] = element

        #entity1: cloud organization - member of entity0 tenant root group

        if entities[1] != None:
            if entities[1]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"].keys():
                element                         = {}
                element["external_id"]          = entities[1]["properties"]["externalId"]              
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["project_id"]           = None
                element["is_folder_project"]    = True
                element["path"]                 = cloud + "/" + entities[0]["name"] + "/" + entities[1]["name"]
                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]] = element

        #entity2: subscription - member of entity1 cloud org
            
        if entities[2] != None:
            if entities[2]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["projects"].keys():                
                element                         = {}
                element["external_id"]          = entities[2]["properties"]["externalId"]             
                element["users"]                = get_role_bindings(entities[2]["properties"]["subscriptionExternalId"], cloud)
                element["project_id"]           = None
                element["is_folder_project"]    = False
                element["path"]                 = cloud + "/" + entities[0]["name"] + "/" + entities[1]["name"] + "/" + entities[2]["name"]

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["projects"][entities[2]["name"]] = element

        #entity3: cloud organization - member of entity1 cloud org

        if entities[3] != None:               
            if entities[3]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"].keys():
                element                         = {}
                element["external_id"]          = entities[3]["properties"]["externalId"]   
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["project_id"]           = None
                element["is_folder_project"]    = True
                element["path"]                 = cloud + "/" + entities[0]["name"] + "/" + entities[1]["name"] + "/" + entities[3]["name"]
                
                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]] = element

        #entity4: subscription - member of entity3 cloud org

        if entities[4] != None:
            if entities[4]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["projects"].keys():
                element                         = {}
                element["external_id"]          = entities[4]["properties"]["externalId"]
                element["users"]                = get_role_bindings(entities[4]["properties"]["subscriptionExternalId"], cloud)
                element["project_id"]           = None
                element["is_folder_project"]    = False
                element["path"]                 = cloud + "/" + entities[0]["name"] + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[4]["name"]

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["projects"][entities[4]["name"]] = element
                    
        #entity5: cloud organization - member of entity3 cloud org
        
        if entities[5] != None:               
            if entities[5]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"].keys():
                element                         = {}
                element["external_id"]          = entities[5]["properties"]["externalId"]
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["project_id"]           = None
                element["is_folder_project"]    = True
                element["path"]                 = cloud + "/" + entities[0]["name"] + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[5]["name"]
                
                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]] = element

        #entity6: subscription - member of entity5 cloud org

        if entities[6] != None:
            if entities[6]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["projects"].keys():
                element                         = {}
                element["external_id"]          = entities[6]["properties"]["externalId"]
                element["users"]                = get_role_bindings(entities[6]["properties"]["subscriptionExternalId"], cloud)
                element["project_id"]           = None
                element["is_folder_project"]    = False
                element["path"]                 = cloud + "/" + entities[0]["name"] + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[5]["name"] + "/" + entities[6]["name"]

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["projects"][entities[6]["name"]] = element

          #entity7: subscription - member of entity0 cloud org

        if entities[7] != None:
            if entities[7]["name"] not in structure["folder_projects"][entities[0]["name"]]["projects"].keys():
                element                         = {}
                element["external_id"]          = entities[7]["properties"]["externalId"]
                element["users"]                = get_role_bindings(entities[7]["properties"]["subscriptionExternalId"], cloud)
                element["project_id"]           = None
                element["is_folder_project"]    = False
                element["path"]                 = cloud + "/" + entities[0]["name"] + "/" + entities[7]["name"]

                structure["folder_projects"][entities[0]["name"]]["projects"][entities[7]["name"]] = element

    structure["folder_projects"] = structure["folder_projects"]

    if burner_mode == True:
        root_burner_structure[cloud]["folder_projects"][mg_friendly_name] = structure
    elif burner_mode == False:
        root_structure[cloud]["folder_projects"][mg_friendly_name] = structure

def process_folder_project(structure, parent_folder_project_id=None, burner_mode=False):

    new_structure = structure["folder_projects"]

    for l1fp in new_structure:
        
        logging.info("Creating folder project: " + new_structure[l1fp]["path"])
        new_structure[l1fp]["project_id"] = mock_create_project(l1fp, new_structure[l1fp]["path"], new_structure[l1fp]["is_folder_project"], parent_folder_project_id, burner_mode)
        logging.info("")

        logging.info("Processing child projects of " + l1fp + "...")
        if new_structure[l1fp]["projects"] == None:
            logging.info("- None found.")

        for project_name in new_structure[l1fp]["projects"]:
            project = new_structure[l1fp]["projects"][project_name]
            logging.info("")
            logging.info("* Creating project: " + l1fp + "/" + project_name)
            new_structure[l1fp]["projects"][project_name]["project_id"] = mock_create_project(project_name, project["path"], False, new_structure[l1fp]["project_id"], burner_mode)

            if len(project["users"].keys()) > 0 and burner_mode == False:
                users = project["users"]
                for user_name in users:
                    mock_provision_user(users[user_name]["display_name"], users[user_name]["email_address"], default_saml_provider, default_user_role, l1fp + "/" + project_name, new_structure[l1fp]["projects"][project_name]["project_id"])
                    add_to_users_dict(users[user_name]["display_name"], users[user_name]["email_address"], default_saml_provider, default_user_role, new_structure[l1fp]["projects"][project_name]["project_id"])
                    logging.info("  - Created User: " + users[user_name]["display_name"] + "(" + users[user_name]["email_address"] + "): " + default_user_role + " on " + l1fp + "/" + project_name)

        logging.info("")
        logging.info("process_folder_project - recursing into next folder project level...")
        new_structure[l1fp]["folder_projects"] = process_folder_project(new_structure[l1fp], new_structure[l1fp]["project_id"], burner_mode)

    structure["folder_projects"] = new_structure

    return new_structure


# mock_create_project(project_path)
# Pretends to create a project in Wiz. Instead just writes the project path it would create to the output txt file.

def mock_create_project(project_name, full_path, is_folder = False, parent_project_id = None, burner_mode = False):

    filename = ""

    if burner_mode == True:
        filename = "mock_project_output_burners.csv"
    else:
        filename = "mock_project_output.csv"

    f = open(filename, "a")

    project_id = project_name + "-0000-0000"

    if parent_project_id == None:
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
    f.write("full_name,role,projects,email,projects_count\n")

    for email_address in users:
        f.write(users[email_address]["display_name"] + "," + users[email_address]["role"] + ",\"" + str(list(users[email_address]["scoped_projects"])) + "\"," + email_address + "," + str(len(users[email_address]["scoped_projects"])) + "\n")

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

    g = open("mock_project_output_burners.csv","w")
    g.write("Project Name,Project Path,Is Folder,Project ID, Parent Project ID\n")


def loop_model_project_structure(burner_mode, cloud, root_mg_list):

    mg_list = json.loads(root_mg_list)

    for mg in mg_list:
        mg_friendly_name = mg["friendly_name"]
        mg_id = mg["group_id"]
        mg_burner_list = mg["burner_list"]

        model_project_structure(burner_mode, mg_id, cloud, mg_friendly_name, mg_burner_list)


def main():

    set_logging_level(log_level)

    logging.info("Getting token.")
    ctwiz.request_wiz_api_token(client_id, client_secret)

    logging.info("Initialising Mock Output Files...")
    initialise_mock_files()

    logging.info("Modelling project structure...")
    loop_model_project_structure(False, "Azure", azure_root_management_group_list)
    loop_model_project_structure(False, "GCP", gcp_root_org_list)
    loop_model_project_structure(False, "AWS", aws_root_org_list)

    logging.info("Creating project structure...")

    #print(root_structure)

    

    root_structure["Azure"] = process_folder_project(root_structure["Azure"], None, False)
    root_structure["GCP"]   = process_folder_project(root_structure["GCP"], None, False)
    root_structure["AWS"]   = process_folder_project(root_structure["AWS"], None, False)

    logging.info("Modelling project structure (burners)...")
    #loop_model_project_structure(True, "Azure", azure_root_management_group_list)
    # Skip GCP burners for now- too many results appears to be the problem here.
    #model_project_structure(True, gcp_organization_id, "GCP")

    logging.info("Creating project structure (burners)...")
    #process_folder_project(root_burner_structure["Azure"], None, True)
    # Skip GCP burners for now- too many results appears to be the problem here.
    #process_folder_project(root_burner_structure["GCP"], None, True)
    # No burner mode needed for AWS

    logging.info("Generating user import file...")
    generate_user_import_file()

if __name__ == '__main__':
    main()