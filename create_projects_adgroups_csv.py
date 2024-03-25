# Filename: create_projects_adgroups_csv.py

# Purpose: Loop through all subscriptions and management groups to build a project structure and output this to a CSV file. 
# Also builds a list of users mapped to respective AD groups and projects, too.

import requests
import json
import sys
import ctwiz
import logging

ARG_CLIENT_ID                   = 1
ARG_CLIENT_SECRET               = 2
ARG_AZURE_ROOT_WIZ_PROJECT_NAME = 3
ARG_AZURE_ROOT_MG_LIST          = 4
ARG_SAML_PROVIDER               = 5
ARG_USER_ROLE                   = 6
ARG_LOG_LEVEL                   = 7
ARG_WIZ_DATACENTER              = 8
ARG_GCP_ROOT_WIZ_PROJECT_NAME   = 9
ARG_GCP_ROOT_ORG_LIST           = 10
ARG_AWS_ROOT_WIZ_PROJECT_NAME   = 11
ARG_AWS_ROOT_ORG_LIST           = 12
ARG_PROJECT_OUTPUT_FILE         = 13
ARG_AD_OUTPUT_FILE              = 14

# Pass in runtime variables
client_id                           = sys.argv[ARG_CLIENT_ID]
client_secret                       = sys.argv[ARG_CLIENT_SECRET]
azure_root_wiz_project_name         = sys.argv[ARG_AZURE_ROOT_WIZ_PROJECT_NAME]
azure_root_management_group_list    = sys.argv[ARG_AZURE_ROOT_MG_LIST]
default_saml_provider               = sys.argv[ARG_SAML_PROVIDER]
default_user_role                   = sys.argv[ARG_USER_ROLE]
log_level                           = sys.argv[ARG_LOG_LEVEL]
wiz_datacenter                      = sys.argv[ARG_WIZ_DATACENTER]
gcp_root_wiz_project_name           = sys.argv[ARG_GCP_ROOT_WIZ_PROJECT_NAME]
gcp_root_org_list                   = sys.argv[ARG_GCP_ROOT_ORG_LIST]
aws_root_wiz_project_name           = sys.argv[ARG_AWS_ROOT_WIZ_PROJECT_NAME]
aws_root_org_list                   = sys.argv[ARG_AWS_ROOT_ORG_LIST]
project_output_file                 = sys.argv[ARG_PROJECT_OUTPUT_FILE]
ad_output_file                      = sys.argv[ARG_AD_OUTPUT_FILE]

# Entity Indexes

azure_entity_matrix= [
    {"index": 0, "entity_type": "cloud_organization", "parent_index": None},
    {"index": 1, "entity_type": "cloud_organization", "parent_index": 0},
    {"index": 2, "entity_type": "subscription", "parent_index": 1},
    {"index": 3, "entity_type": "cloud_organization", "parent_index": 1},
    {"index": 4, "entity_type": "subscription", "parent_index": 3},
    {"index": 5, "entity_type": "cloud_organization", "parent_index": 3},
    {"index": 6, "entity_type": "subscription", "parent_index": 5},
    {"index": 7, "entity_type": "cloud_organization", "parent_index": 5},
    {"index": 8, "entity_type": "cloud_organization", "parent_index": 7},
    {"index": 9, "entity_type": "cloud_organization", "parent_index": 8},
    {"index": 10, "entity_type": "subscription", "parent_index": 9},
    {"index": 11, "entity_type": "subscription", "parent_index": 8},
    {"index": 12, "entity_type": "subscription", "parent_index": 7},
    {"index": 13, "entity_type": "subscription", "parent_index": 0},
]

aws_entity_matrix = [
    {"index": 0, "entity_type": "cloud_organization", "parent_index": None},
    {"index": 1, "entity_type": "cloud_organization", "parent_index": 0},
    {"index": 2, "entity_type": "subscription", "parent_index": 1},
    {"index": 3, "entity_type": "cloud_organization", "parent_index": 1},
    {"index": 4, "entity_type": "subscription", "parent_index": 3},
    {"index": 5, "entity_type": "cloud_organization", "parent_index": 3},
    {"index": 6, "entity_type": "subscription", "parent_index": 5},
    {"index": 7, "entity_type": "cloud_organization", "parent_index": 5},
    {"index": 8, "entity_type": "cloud_organization", "parent_index": 7},
    {"index": 9, "entity_type": "cloud_organization", "parent_index": 8},
    {"index": 10, "entity_type": "subscription", "parent_index": 9},
    {"index": 11, "entity_type": "subscription", "parent_index": 8},
    {"index": 12, "entity_type": "subscription", "parent_index": 7},
    {"index": 13, "entity_type": "subscription", "parent_index": 0},
]

gcp_entity_matrix = [
    {"index": 0, "entity_type": "cloud_organization", "parent_index": None},
    {"index": 1, "entity_type": "cloud_organization", "parent_index": 0},
    {"index": 2, "entity_type": "subscription", "parent_index": 1},
    {"index": 3, "entity_type": "cloud_organization", "parent_index": 1},
    {"index": 4, "entity_type": "subscription", "parent_index": 3},
    {"index": 5, "entity_type": "cloud_organization", "parent_index": 3},
    {"index": 6, "entity_type": "subscription", "parent_index": 5},
    {"index": 7, "entity_type": "cloud_organization", "parent_index": 5},
    {"index": 8, "entity_type": "subscription", "parent_index": 7},
    {"index": 9, "entity_type": "subscription", "parent_index": 0},
]

def get_matrix(cloud):
    if cloud == "Azure":
        return azure_entity_matrix
    elif cloud == "AWS":
        return aws_entity_matrix
    elif cloud == "GCP":
        return gcp_entity_matrix

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

groups = {}

root_structure = {}

root_burner_structure = {}

root_burner_structure["Azure"] = {}
root_burner_structure["Azure"]["folder_projects"] = {}
root_burner_structure["Azure"]["projects"]        = {}
root_burner_structure["Azure"]["is_folder_project"] = True

root_burner_structure["GCP"]   = {}
root_burner_structure["GCP"]["folder_projects"] = {}
root_burner_structure["GCP"]["projects"]        = {}
root_burner_structure["GCP"]["is_folder_project"] = True

def build_root_structure():

    aws_org_list = json.loads(aws_root_org_list)

    if len(aws_org_list) > 0:
        root_structure[aws_root_wiz_project_name]                           = {}
        root_structure[aws_root_wiz_project_name]["name"]                   = aws_root_wiz_project_name
        root_structure[aws_root_wiz_project_name]["folder_projects"]        = {}
        root_structure[aws_root_wiz_project_name]["projects"]               = {}
        root_structure[aws_root_wiz_project_name]["is_folder_project"]      = True
        root_structure[aws_root_wiz_project_name]["path"]                   = aws_root_wiz_project_name
        root_structure[aws_root_wiz_project_name]["parent_project_name"]    = "ROOT"

        write_to_project_file(aws_root_wiz_project_name, None, aws_root_wiz_project_name, root_structure[aws_root_wiz_project_name]["is_folder_project"], None, "AWS")

        for aws_org in aws_org_list:
            if aws_org["burner_list"]:
                root_burner_structure["AWS"] = {}
                root_burner_structure["AWS"]["folder_projects"] = {}
                root_burner_structure["AWS"]["projects"]        = {}
                root_burner_structure["AWS"]["is_folder_project"] = True
                break

    azure_org_list = json.loads(azure_root_management_group_list)

    if len(azure_org_list) > 0:
        root_structure[azure_root_wiz_project_name] = {}
        root_structure[azure_root_wiz_project_name]["name"]                 = azure_root_wiz_project_name
        root_structure[azure_root_wiz_project_name]["folder_projects"]      = {}
        root_structure[azure_root_wiz_project_name]["projects"]             = {}
        root_structure[azure_root_wiz_project_name]["is_folder_project"]    = True
        root_structure[azure_root_wiz_project_name]["path"]                 = azure_root_wiz_project_name
        root_structure[azure_root_wiz_project_name]["parent_project_id"]    = "ROOT"

        write_to_project_file(azure_root_wiz_project_name, None, azure_root_wiz_project_name, root_structure[azure_root_wiz_project_name]["is_folder_project"], None, "Azure")

        for azure_org in azure_org_list:
            if azure_org["burner_list"]:
                root_burner_structure["Azure"] = {}
                root_burner_structure["Azure"]["folder_projects"] = {}
                root_burner_structure["Azure"]["projects"]        = {}
                root_burner_structure["Azure"]["is_folder_project"] = True
                break

    gcp_org_list = json.loads(gcp_root_org_list)

    if len(gcp_org_list) > 0:
        root_structure[gcp_root_wiz_project_name]                       = {}
        root_structure[gcp_root_wiz_project_name]["name"]               = gcp_root_wiz_project_name
        root_structure[gcp_root_wiz_project_name]["folder_projects"]    = {}
        root_structure[gcp_root_wiz_project_name]["projects"]           = {}
        root_structure[gcp_root_wiz_project_name]["is_folder_project"]  = True
        root_structure[gcp_root_wiz_project_name]["path"]               = gcp_root_wiz_project_name
        root_structure[gcp_root_wiz_project_name]["parent_project_id"]  = "ROOT"

        write_to_project_file(gcp_root_wiz_project_name, None, gcp_root_wiz_project_name, root_structure[gcp_root_wiz_project_name]["is_folder_project"], None, "GCP")

        for gcp_org in gcp_org_list:
            if gcp_org["burner_list"]:
                root_burner_structure["GCP"] = {}
                root_burner_structure["GCP"]["folder_projects"] = {}
                root_burner_structure["GCP"]["projects"]        = {}
                root_burner_structure["GCP"]["is_folder_project"] = True
                break
    
def get_group_members(external_id, scope_type, cloud):

    query       = ctwiz.get_qry_grp_role_bindings()
    variables   = ""
    # Adding to dict to ensure duplicate results won't be added.
    group_member_list = []

    if cloud == "AWS" and scope_type == "subscription":
        variables   = ctwiz.get_qry_vars_grp_members_for_subscriptions(external_id, cloud)
    elif cloud == "AWS" and scope_type == "cloud_organization":
        # logging.info("No role bindings for AWS OUs")
        return group_member_list
    elif cloud == "Azure" and scope_type == "subscription":
        variables   = ctwiz.get_qry_vars_grp_members_for_subscriptions(external_id, cloud)
    elif cloud == "Azure" and scope_type == "cloud_organization":
        variables   = ctwiz.get_qry_vars_grp_members_for_mgmt_groups(external_id, cloud)
    elif cloud == "GCP" and scope_type == "subscription":
        variables   = ctwiz.get_qry_vars_grp_members_for_subscriptions(external_id, cloud)
    elif cloud == "GCP" and scope_type == "cloud_organization":
        variables   = ctwiz.get_qry_vars_grp_members_for_mgmt_groups(external_id, cloud)

    results     = ctwiz.query_wiz_api(query, variables, wiz_datacenter)

    # Pagination
    page_info = results["data"]["graphSearch"]["pageInfo"]

    while(page_info["hasNextPage"]):
        logging.info("Paginating on get_role_bindings")
        variables["after"] = page_info["endCursor"]
        this_results = ctwiz.query_wiz_api(query, variables, wiz_datacenter)
        results["data"]["graphSearch"]["nodes"].extend(this_results["data"]["graphSearch"]["nodes"])
        page_info = this_results["data"]["graphSearch"]["pageInfo"]

    for result in results["data"]["graphSearch"]["nodes"]:

        entities = result["entities"]

        member = {}
        member["name"] = entities[0]["properties"]["name"]
        if cloud == "GCP" or cloud == "AWS":
            member["email"] = entities[0]["properties"]["name"]
        else:
            member["email"] = entities[0]["properties"]["userPrincipalName"]

        group_member_list.append(member)

    return group_member_list

def write_ad_group_to_file(group_name, project_name, members_list, cloud):
    
    f = open(ad_output_file, "a")

    for member in members_list:
        f.write("\"" + group_name + "\",\"" + project_name + "\",\"" + member["name"] + "\",\"" + member["email"] + "\",\"" + cloud + "\"\n")

def new_project_element(external_id, project_name, element_type, parent_project_name, burner_mode, entity_path, cloud):
    element                                 = {}
    element["external_id"]                  = external_id
    element["name"]                         = project_name
    element["groups"]                       = {}
    element["path"]                         = entity_path
    element["parent_project_name"]          = parent_project_name
    element["ad_groups"]                    = {}

    if element_type == "cloud_organization":
        element["folder_projects"]      = {}
        element["projects"]             = {}
        element["is_folder_project"]    = True
        write_to_project_file(project_name, external_id, element["path"], element["is_folder_project"], parent_project_name, cloud)
    elif element_type == "subscription":
        element["is_folder_project"]    = False
        write_to_project_file(project_name, external_id, element["path"], element["is_folder_project"], parent_project_name, cloud)

    for group_id in ["Wiz_" + str(project_name + "_" + default_user_role)]:
        element["ad_groups"][group_id] = {} 
        element["ad_groups"][group_id]["members"] = get_group_members(external_id, element_type, cloud)

        write_ad_group_to_file(group_id, project_name, element["ad_groups"][group_id]["members"], cloud)

    return element


def get_entity_lineage_matrix(cloud, target_index, result_list):

    matrix = get_matrix(cloud)

    if result_list == None:
        
        result_list = [target_index]

    if target_index == 0:
        return result_list

    for entity in matrix:
        if entity["index"] == target_index:
            return get_entity_lineage_matrix(cloud, entity["parent_index"], [entity["parent_index"]] + result_list)

def build_entity_lineage(cloud, entity_index, entities, mg_friendly_name):

    entity_lineage_matrix = get_entity_lineage_matrix(cloud, entity_index, None)
    entity_name_lineage_list = []

    for entry in entity_lineage_matrix:
        if entity_lineage_matrix.index(entry) == 0:
            name = mg_friendly_name
        else:
            if entities[entry]["name"].find("/") != -1:
                name = entities[entry]["name"].replace("/","-")
            else:
                name = entities[entry]["name"]

        entity_name_lineage_list = entity_name_lineage_list + [name]

    return entity_name_lineage_list

def find_or_create_cloud_org(this_project, target_entity_index, target_entity_name, target_entity_lineage, target_entity_external_id, burner_mode, entity_path, cloud, parent_project_name):

    next_entity_lineage = None
    if len(target_entity_lineage) > 0:
        next_entity_lineage = target_entity_lineage.pop(0)

    # Are we at the correct entity_lineage and is the current project a folder project?
    if len(target_entity_lineage) == 0 and next_entity_lineage == target_entity_name and this_project["is_folder_project"] == True:

        # Return this project if the target folder project already exists within this folder project
        if next_entity_lineage in this_project["folder_projects"].keys():
            return this_project
        else:
            # Create new project element here if it doesn't already exists and should exist here
            parent_project_name = this_project["name"]
            this_project["folder_projects"][next_entity_lineage] = new_project_element(target_entity_external_id, target_entity_name, "cloud_organization", parent_project_name, burner_mode, entity_path, cloud)
            return this_project
    # Have we stumbled across a project instead of a folder project within the structure? If so return back this_project
    elif this_project["is_folder_project"] == False:
        return this_project

    # Do we still have further lineage to traverse and is the current project a folder project?
    if len(target_entity_lineage) > 0 and this_project["is_folder_project"] == True:

        # Recurse if the target next entity lineage
        if next_entity_lineage in this_project["folder_projects"].keys():
            # print("Recursing find_or_create_cloud_org....")
            parent_project_name = this_project["name"]
            this_project["folder_projects"][next_entity_lineage] = find_or_create_cloud_org(this_project["folder_projects"][next_entity_lineage], target_entity_index, target_entity_name, target_entity_lineage, target_entity_external_id, burner_mode, entity_path, cloud, parent_project_name)
            return this_project

    return this_project

def find_or_create_subscription(this_project, target_entity_index, target_entity_name, target_entity_lineage, target_entity_external_id, burner_mode, entity_path, cloud, parent_project_id):

    next_entity_lineage = None
    if len(target_entity_lineage) > 0:
        next_entity_lineage = target_entity_lineage.pop(0)

    # Create new project element if it doesn't exist
    if len(target_entity_lineage) == 0 and next_entity_lineage == target_entity_name:

        # Return project if it already exists
        if next_entity_lineage in this_project["projects"].keys():
            return this_project
        
        # Create new project if it doesn't exist
        else:
            parent_project_name = this_project["name"]
            this_project["projects"][next_entity_lineage] = new_project_element(target_entity_external_id, target_entity_name, "subscription", parent_project_name, burner_mode, entity_path, cloud)
            return this_project

    # Next entity lineage is within this folder project, so we'll need to recurse down to it
    if len(target_entity_lineage) > 0 and this_project["is_folder_project"] == True:
        if next_entity_lineage in this_project["folder_projects"].keys():
            parent_project_name = this_project["name"]
            # print("Recursing find_or_create_subscription...")
            this_project["folder_projects"][next_entity_lineage] = find_or_create_subscription(this_project["folder_projects"][next_entity_lineage], target_entity_index, target_entity_name, target_entity_lineage, target_entity_external_id, burner_mode, entity_path, cloud, parent_project_name)
            return this_project


def model_project_structure(burner_mode, root_mg_id, cloud, mg_friendly_name, mg_burner_list):

    logging.info("Cloud: " + cloud + " - Burner Mode: " + str(burner_mode) + " - Root Mgmt Group: " + root_mg_id)
    query       = ctwiz.get_qry_project_structure()
    variables   = {}
    root_wiz_project_name = ""
    
    if burner_mode      == True and cloud == "Azure" and len(mg_burner_list) != 0:
        variables   = ctwiz.get_qry_vars_azure_project_structure_burners(root_mg_id, mg_burner_list[0])
        root_wiz_project_name = azure_root_wiz_project_name
    elif burner_mode    == False and cloud == "Azure" and len(mg_burner_list) != 0:
        variables  = ctwiz.get_qry_vars_azure_project_structure_excl_burners(root_mg_id, mg_burner_list[0])
        root_wiz_project_name = azure_root_wiz_project_name 
    elif burner_mode    == False and cloud == "Azure" and len(mg_burner_list) == 0:
        root_wiz_project_name = azure_root_wiz_project_name
        variables  = ctwiz.get_qry_vars_project_structure_no_burners(root_mg_id, cloud)
    elif burner_mode    == True and cloud == "GCP":
        root_wiz_project_name = cloud
        logging.info("Not catering for GCP burners - too many results to process. They will be excluded from project creation and should be added to a new project manually later on")
        return None
    elif burner_mode    == False and cloud == "GCP" and len(mg_burner_list) > 0:
        root_wiz_project_name = gcp_root_wiz_project_name
        variables   = ctwiz.get_qry_vars_gcp_project_structure_excl_burners(root_mg_id, mg_burner_list[0])
    elif burner_mode    == False and cloud == "GCP" and len(mg_burner_list) == 0:
        root_wiz_project_name = gcp_root_wiz_project_name
        variables   = ctwiz.get_qry_vars_gcp_project_structure_excl_burners(root_mg_id, "")        
    elif burner_mode    == True and cloud == "AWS":
        logging.info("No burner mode for AWS")
        return None
    elif burner_mode    == False and cloud == "AWS":
        root_wiz_project_name = aws_root_wiz_project_name
        variables  = ctwiz.get_qry_vars_project_structure_no_burners(root_mg_id, cloud)
    
    results     = ctwiz.query_wiz_api(query, variables, wiz_datacenter)

    # Pagination
    page_info = results["data"]["graphSearch"]["pageInfo"]
    try:
        while(page_info["hasNextPage"]):
            logging.info("Paginating on model_project_structure")
            variables["after"] = page_info["endCursor"]
            this_results = ctwiz.query_wiz_api(query, variables, wiz_datacenter)
            results["data"]["graphSearch"]["nodes"].extend(this_results["data"]["graphSearch"]["nodes"])
            page_info = this_results["data"]["graphSearch"]["pageInfo"]
    except TypeError:
        logging.info("Hit 10k results limit")

    logging.info("Exited Pagination")

    logging.info(str(len(results["data"]["graphSearch"]["nodes"])) + " Results fetched")
    
    matrix = get_matrix(cloud)

    i = 0
    for result in results["data"]["graphSearch"]["nodes"]:
        i = i + 1

        if i == 11:
            break

        logging.info("Processing result " + str(i) + " of " + str(len(results["data"]["graphSearch"]["nodes"])))

        entities = result["entities"]

        for entity in entities:

            if entity != None:
                entity_index        = entities.index(entity)
                entity_type         = matrix[entity_index]["entity_type"]
                entity_name         = None
                parent_project_name = None

                if entity_index == 0:
                    entity_name         = mg_friendly_name
                    parent_project_name = root_structure[root_wiz_project_name]["name"]
                else:
                    # Projects with forward-slashes in name confuse are not accepted. Substitute forward-slashes for dashes
                    if entity["name"].find("/") != -1:
                        entity_name = entity["name"].replace("/","-")
                    else:
                        entity_name = entity["name"]

                entity_lineage  =  build_entity_lineage(cloud, entity_index, entities, mg_friendly_name)
                entity_path         = root_wiz_project_name + "/" + "/".join(entity_lineage)
                entity_external_id  = entity["properties"]["externalId"]

                if entity_type == "cloud_organization":

                    root_structure[root_wiz_project_name] = find_or_create_cloud_org(root_structure[root_wiz_project_name], entity_index, entity_name, entity_lineage, entity_external_id, burner_mode, entity_path, cloud, parent_project_name)

                elif entity_type == "subscription":

                    root_structure[root_wiz_project_name] = find_or_create_subscription(root_structure[root_wiz_project_name], entity_index, entity_name, entity_lineage, entity_external_id, burner_mode, entity_path, cloud, parent_project_name)

# write_to_project_file()
# Writes a line representing this project/folder project to the project output file CSV

def write_to_project_file(project_name, external_id, full_path, is_folder, parent_project_name, cloud):

    path_depth = len(full_path.split("/"))

    f = open(project_output_file, "a")

    if parent_project_name == None:
        f.write("\"" + project_name + "\",\"" + str(is_folder)  + "\",\"" + str(external_id) + "\",,,\"" + full_path + "\",\"" + str(path_depth) + "\",\"" + cloud +"\"\n")
    else:
        f.write("\"" + project_name + "\",\"" + str(is_folder)  + "\",\"" + str(external_id) + "\",,\"" + parent_project_name + "\",\"" + full_path + "\",\"" + str(path_depth) + "\",\"" + cloud +"\"\n")


def initialise_mock_files():
    g = open(project_output_file,"w")
    g.write("wiz-project-name,isFolder,cloudAccountLinks,cloudOrganizationLinks,parentProjectName,Full Path,Path Depth,Cloud\n")

    g = open(ad_output_file,"w")
    g.write("Group Name,Wiz Project,Member Name,Member UPN/Email,Originating Cloud\n")


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
    build_root_structure()
    loop_model_project_structure(False, "Azure", azure_root_management_group_list)
    loop_model_project_structure(False, "GCP", gcp_root_org_list)
    loop_model_project_structure(False, "AWS", aws_root_org_list)

    # Might just skip burners all together. They can always be added manually later on.
    #logging.info("Modelling project structure (burners)...")
    #loop_model_project_structure(True, "Azure", azure_root_management_group_list)
    # Skip GCP burners for now- too many results appears to be the problem here.
    #model_project_structure(True, gcp_organization_id, "GCP")

if __name__ == '__main__':
    main()