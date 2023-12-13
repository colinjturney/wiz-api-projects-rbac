# Filename: create_folder_projects.py
# Purpose: Loop through all Azure Management Groups that are children of a defined management group and create folder projects for them.
#          Note: Top-level management groups will have folder projects created prepended with Azure-

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
        root_structure[aws_root_wiz_project_name]                       = {}
        root_structure[aws_root_wiz_project_name]["folder_projects"]    = {}
        root_structure[aws_root_wiz_project_name]["projects"]           = {}
        root_structure[aws_root_wiz_project_name]["is_folder_project"]  = True
        root_structure[aws_root_wiz_project_name]["path"]               = aws_root_wiz_project_name + "/"
        root_structure[aws_root_wiz_project_name]["project_id"]         = mock_create_project("AWS_Root", aws_root_wiz_project_name, root_structure[aws_root_wiz_project_name]["path"], root_structure[aws_root_wiz_project_name]["is_folder_project"], None, False)

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
        root_structure[azure_root_wiz_project_name]["folder_projects"]      = {}
        root_structure[azure_root_wiz_project_name]["projects"]             = {}
        root_structure[azure_root_wiz_project_name]["is_folder_project"]    = True
        root_structure[azure_root_wiz_project_name]["path"]                 = azure_root_wiz_project_name + "/"
        root_structure[azure_root_wiz_project_name]["project_id"]           = mock_create_project("Azure_Root", azure_root_wiz_project_name, root_structure[azure_root_wiz_project_name]["path"], root_structure[azure_root_wiz_project_name]["is_folder_project"], None, False)

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
        root_structure[gcp_root_wiz_project_name]["folder_projects"]    = {}
        root_structure[gcp_root_wiz_project_name]["projects"]           = {}
        root_structure[gcp_root_wiz_project_name]["is_folder_project"]  = True
        root_structure[gcp_root_wiz_project_name]["path"]               = gcp_root_wiz_project_name + "/"
        root_structure[gcp_root_wiz_project_name]["project_id"]         = mock_create_project("GCP_Root", gcp_root_wiz_project_name, root_structure[gcp_root_wiz_project_name]["path"], root_structure[gcp_root_wiz_project_name]["is_folder_project"], None, False)

        for gcp_org in gcp_org_list:
            if gcp_org["burner_list"]:
                root_burner_structure["GCP"] = {}
                root_burner_structure["GCP"]["folder_projects"] = {}
                root_burner_structure["GCP"]["projects"]        = {}
                root_burner_structure["GCP"]["is_folder_project"] = True
                break


def get_group_role_bindings(id, scope_type, project_id, cloud):

    query       = ctwiz.get_qry_grp_role_bindings()
    variables   = ""

    if cloud == "AWS" and scope_type == "subscription":
        variables   = ctwiz.get_qry_vars_grp_aws_role_bindings_for_subscriptions(id)
    elif cloud == "AWS" and scope_type == "management_group":
        logging.info("No role bindings for AWS OUs")
    elif cloud == "Azure" and scope_type == "subscription":
        variables   = ctwiz.get_qry_vars_grp_azure_role_bindings_for_subscriptions(id)
    elif cloud == "Azure" and scope_type == "management_group":
        variables   = ctwiz.get_qry_vars_grp_azure_role_bindings_for_mgmtgrp(id)
    elif cloud == "GCP" and scope_type == "subscription":
        #variables   = ctwiz.get_qry_vars_grp_azure_role_bindings_for_subscriptions(id)
        logging.info("GCP not yet supported for group role bindings...")
        exit(1)
    elif cloud == "GCP" and scope_type == "management_group":
        #variables   = ctwiz.get_qry_vars_grp_azure_role_bindings_for_mgmtgrp(id)
        logging.info("GCP not yet supported for group role bindings...")
        exit(1)

    results     = ctwiz.query_wiz_api(query, variables, wiz_datacenter)

    try:
        # Pagination
        page_info = results["data"]["graphSearch"]["pageInfo"]

        while(page_info["hasNextPage"]):
            logging.info("Paginating on get_role_bindings")
            variables["after"] = page_info["endCursor"]
            this_results = ctwiz.query_wiz_api(query, variables, wiz_datacenter)
            results["data"]["graphSearch"]["nodes"].extend(this_results["data"]["graphSearch"]["nodes"])
            page_info = this_results["data"]["graphSearch"]["pageInfo"]

        # Adding to dict to ensure duplicate results won't be added.
        group_project_bindings = {}

        for result in results["data"]["graphSearch"]["nodes"]:

            entities = result["entities"]

            group_name  = entities[0]["properties"]["name"]
            group_id    = entities[0]["properties"]["externalId"]

            try:
                if groups[group_id] != None:
                    groups[group_id]["scoped_projects"].append(project_id)
            except KeyError:
                new_group = {}
                new_group["group_name"] = group_name
                new_group["group_id"]   = group_id
                new_group["scoped_projects"] = [project_id]
                new_group["scope_type"] = scope_type
                groups[group_id] = new_group

            if entities[0] != None:
                group_project_bindings[group_id] = {
                    "group_name" : group_name,
                    "group_id"  : group_id
                }

        return group_project_bindings

    except KeyError:
        logging.info("No role bindings for AWS OUs")
        return {}

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
        variables   = ctwiz.get_qry_vars_gcp_project_structure_burners(root_mg_id, mg_burner_list[0])
    elif burner_mode    == False and cloud == "GCP":
        root_wiz_project_name = gcp_root_wiz_project_name
        variables   = ctwiz.get_qry_vars_gcp_project_structure_excl_burners(root_mg_id, mg_burner_list[0])
    elif burner_mode    == True and cloud == "AWS":
        logging.info("No burner mode for AWS")
        return None
    elif burner_mode    == False and cloud == "AWS":
        root_wiz_project_name = aws_root_wiz_project_name
        variables  = ctwiz.get_qry_vars_project_structure_no_burners(root_mg_id, cloud)
    
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

        if i == 51:
            break

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
                element["is_folder_project"]    = True
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name
                element["project_id"]           = mock_create_project(entities[0]["properties"]["externalId"], mg_friendly_name, element["path"], element["is_folder_project"], root_structure[root_wiz_project_name]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[0]["properties"]["externalId"], "management_group", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]] = element

        #entity1: cloud organization - member of entity0 tenant root group

        if entities[1] != None:
            if entities[1]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"].keys():
                element                         = {}
                element["external_id"]          = entities[1]["properties"]["externalId"]              
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["is_folder_project"]    = True
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"]
                element["project_id"]           = mock_create_project(entities[1]["properties"]["externalId"], entities[1]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[1]["properties"]["externalId"], "management_group", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]] = element

        #entity2: subscription - member of entity1 cloud org
            
        if entities[2] != None:
            if entities[2]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["projects"].keys():                
                element                         = {}
                element["external_id"]          = entities[2]["properties"]["externalId"]
                element["is_folder_project"]    = False
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[2]["name"]
                element["project_id"]           = mock_create_project(entities[2]["properties"]["externalId"], entities[2]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[2]["properties"]["subscriptionExternalId"], "subscription", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["projects"][entities[2]["name"]] = element

        #entity3: cloud organization - member of entity1 cloud org

        if entities[3] != None:               
            if entities[3]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"].keys():
                element                         = {}
                element["external_id"]          = entities[3]["properties"]["externalId"]   
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["is_folder_project"]    = True  
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[3]["name"]
                element["project_id"]           = mock_create_project(entities[3]["properties"]["externalId"], entities[3]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[3]["properties"]["externalId"], "management_group", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]] = element

        #entity4: subscription - member of entity3 cloud org

        if entities[4] != None:
            if entities[4]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["projects"].keys():
                element                         = {}
                element["external_id"]          = entities[4]["properties"]["externalId"]
                element["is_folder_project"]    = False
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[4]["name"]
                element["project_id"]           = mock_create_project(entities[4]["properties"]["externalId"], entities[4]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[4]["properties"]["subscriptionExternalId"], "subscription", element["project_id"], cloud)
 
                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["projects"][entities[4]["name"]] = element
                    
        #entity5: cloud organization - member of entity3 cloud org
        
        if entities[5] != None:               
            if entities[5]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"].keys():
                element                         = {}
                element["external_id"]          = entities[5]["properties"]["externalId"]
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["is_folder_project"]    = True
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[5]["name"]
                element["project_id"]           = mock_create_project(entities[5]["properties"]["externalId"], entities[5]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[5]["properties"]["externalId"], "management_group", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]] = element

        #entity6: subscription - member of entity5 cloud org

        if entities[6] != None:
            if entities[6]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["projects"].keys():
                element                         = {}
                element["external_id"]          = entities[6]["properties"]["externalId"]
                element["is_folder_project"]    = False
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[5]["name"] + "/" + entities[6]["name"]
                element["project_id"]           = mock_create_project(entities[6]["properties"]["externalId"], entities[6]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[6]["properties"]["subscriptionExternalId"], "subscription", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["projects"][entities[6]["name"]] = element

        #entity7: cloud organization - member of entity5 cloud org

        if entities[7] != None:
            if entities[7]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"].keys():
                element                         = {}
                element["external_id"]          = entities[7]["properties"]["externalId"]
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["is_folder_project"]    = True
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[5]["name"] + "/" + entities[7]["name"]
                element["project_id"]           = mock_create_project(entities[7]["properties"]["externalId"], entities[7]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[7]["properties"]["externalId"], "management_group", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]] = element

        #entity8: cloud organization - member of entity7 cloud org

        if entities[8] != None:
            if entities[8]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["folder_projects"].keys():
                element                         = {}
                element["external_id"]          = entities[8]["properties"]["externalId"]
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["is_folder_project"]    = True
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[5]["name"] + "/" + entities[7]["name"] + "/" + entities[8]["name"]
                element["project_id"]           = mock_create_project(entities[8]["properties"]["externalId"], entities[8]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["project_id"]], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[8]["properties"]["externalId"], "management_group", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["folder_projects"][entities[8]["name"]] = element

        #entity9: cloud organization - member of entity8 cloud org

        if entities[9] != None:
            if entities[9]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["folder_projects"][entities[8]["name"]["folder_projects"]].keys():
                element                         = {}
                element["external_id"]          = entities[9]["properties"]["externalId"]
                element["folder_projects"]      = {}
                element["projects"]             = {}
                element["is_folder_project"]    = True
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[5]["name"] + "/" + entities[7]["name"] + "/" + entities[8]["name"] + "/" + entities[9]["name"]
                element["project_id"]           = mock_create_project(entities[9]["properties"]["externalId"], entities[9]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]["folder_projects"][entities[8]["name"]["project_id"]]], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[9]["properties"]["externalId"], "management_group", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["folder_projects"][entities[8]["name"]]["folder_projects"][entities[9]["name"]] = element

        #entity10: subscription - member of entity9 cloud org

        if entities[10] != None:
            if entities[10]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["projects"]["folder_projects"][entities[7]["name"]]["folder_projects"][entities[8]["name"]]["folder_projects"][entities[9]["name"]]["projects"].keys():
                element                         = {}
                element["external_id"]          = entities[10]["properties"]["externalId"]
                element["is_folder_project"]    = False
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[5]["name"] + "/" + entities[7]["name"] + "/" + entities[8]["name"] + "/" + entities[9]["name"] + "/" + entities[10]["name"]
                element["project_id"]           = mock_create_project(entities[10]["properties"]["externalId"], entities[10]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["folder_projects"][entities[8]["name"]]["folder_projects"][entities[9]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[10]["properties"]["subscriptionExternalId"], "subscription", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["folder_projects"][entities[8]["name"]]["folder_projects"][entities[9]["name"]]["projects"][entities[10]["name"]] = element

        #entity11: subscription - member of entity8 cloud org

        if entities[11] != None:
            if entities[11]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["folder_projects"][entities[8]["name"]]["projects"].keys():
                element                         = {}
                element["external_id"]          = entities[11]["properties"]["externalId"]
                element["is_folder_project"]    = False
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[5]["name"] + "/" + entities[7]["name"] + "/" + entities[8]["name"] + "/" + entities[11]["name"]
                element["project_id"]           = mock_create_project(entities[11]["properties"]["externalId"], entities[11]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["folder_projects"][entities[8]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[11]["properties"]["subscriptionExternalId"], "subscription", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["folder_projects"][entities[8]["name"]]["projects"][entities[11]["name"]] = element

         #entity12: subscription - member of entity7 cloud org

        if entities[12] != None:
            if entities[12]["name"] not in structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["projects"].keys():
                element                         = {}
                element["external_id"]          = entities[12]["properties"]["externalId"]
                element["is_folder_project"]    = False
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[1]["name"] + "/" + entities[3]["name"] + "/" + entities[5]["name"] + "/" + entities[7]["name"] + "/" + entities[12]["name"]
                element["project_id"]           = mock_create_project(entities[12]["properties"]["externalId"], entities[12]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[12]["properties"]["subscriptionExternalId"], "subscription", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["folder_projects"][entities[1]["name"]]["folder_projects"][entities[3]["name"]]["folder_projects"][entities[5]["name"]]["folder_projects"][entities[7]["name"]]["projects"][entities[12]["name"]] = element
        
        #entity13: subscription - member of entity0 cloud org

        if entities[13] != None:
            if entities[13]["name"] not in structure["folder_projects"][entities[0]["name"]]["projects"].keys():
                element                         = {}
                element["external_id"]          = entities[13]["properties"]["externalId"]
                element["is_folder_project"]    = False
                element["path"]                 = root_wiz_project_name + "/" + mg_friendly_name + "/" + entities[13]["name"]
                element["project_id"]           = mock_create_project(entities[13]["properties"]["externalId"], entities[13]["name"], element["path"], element["is_folder_project"], structure["folder_projects"][entities[0]["name"]]["project_id"], burner_mode)
                element["groups"]               = get_group_role_bindings(entities[13]["properties"]["subscriptionExternalId"], "subscription", element["project_id"], cloud)

                structure["folder_projects"][entities[0]["name"]]["projects"][entities[13]["name"]] = element

    structure["folder_projects"] = structure["folder_projects"]

    if burner_mode == True:
        root_burner_structure[root_wiz_project_name]["folder_projects"][mg_friendly_name] = structure
    elif burner_mode == False:
        root_structure[root_wiz_project_name]["folder_projects"][mg_friendly_name] = structure


# mock_create_project(project_path)
# Pretends to create a project in Wiz. Instead just writes the project path it would create to the output txt file.

def mock_create_project(external_id, project_name, full_path, is_folder = False, parent_project_id = None, burner_mode = False):

    filename = ""

    if burner_mode == True:
        filename = "mock_project_output_burners.csv"
    else:
        filename = "mock_project_output.csv"

    f = open(filename, "a")

    project_id = project_name + "-0000-0000"

    if parent_project_id == None:
        f.write("\"" + project_name + "\",\"" + external_id + "\",\"" + full_path + "\"," + str(is_folder) + "," + project_id + "\n")
    else:
        f.write("\"" + project_name + "\",\"" + external_id + "\",\"" + full_path + "\"," + str(is_folder) + "," + project_id + "," + parent_project_id + "\n")

    return project_id

def create_project(external_id, project_name, is_folder, parent_project_id):

    query       = ctwiz.get_qry_project_structure()
    variables   = {}

    if is_folder == True:

        if parent_project_id == None:
            variables = ctwiz.get_qry_vars_create_folder_project(project_name, "")

        elif parent_project_id != None:
            variables = ctwiz.get_qry_vars_create_folder_project(project_name, parent_project_id)

    elif is_folder == False:
        variables = ctwiz.get_qry_vars_create_project_subscription(project_name, external_id, parent_project_id)

    results     = ctwiz.query_wiz_api(query, variables, wiz_datacenter)

    project_id = results["data"]["createProject"]["project"]["id"]

    return project_id

def write_saml_role_mappings():
    f = open("saml_role_mappings.csv","a")

    for group_id in groups:
        f.write(group_id + "," + groups[group_id]["group_name"] + "," + default_user_role + ",\"" + str(groups[group_id]["scoped_projects"]) + "\"," + str(len(groups[group_id]["scoped_projects"])) + "\n")

def initialise_mock_files():
    f = open("saml_role_mappings.csv","w")
    f.write("Group ID, Group Name, Role, Projects, Scoped Project Count\n")
 
    g = open("mock_project_output.csv","w")
    g.write("Project Name,External ID, Project Path,Is Folder,Project ID, Parent Project ID\n")

    g = open("mock_project_output_burners.csv","w")
    g.write("Project Name,External ID, Project Path,Is Folder,Project ID, Parent Project ID\n")


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

    logging.info("Writing SAML Role Mappings Files...")
    write_saml_role_mappings()

if __name__ == '__main__':
    main()