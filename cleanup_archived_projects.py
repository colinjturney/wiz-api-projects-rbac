# Filename: cleanup_archived_projects.py
# Purpose: Loop through all Azure Management Groups that are children of a defined management group and create folder projects for them.
#          Note: Top-level management groups will have folder projects created prepended with Azure-

import requests
import json
import sys
import ctwiz
import logging

ARG_CLIENT_ID                   = 1
ARG_CLIENT_SECRET               = 2
ARG_ROOT_PROJECT_ID             = 3
ARG_INCLUDE_ARCHIVED            = 4
ARG_PROJECT_NAME_SUFFIX         = 5
ARG_SLUG_SUFFIX                 = 6
ARG_SET_ARCHIVE_STATUS          = 7
ARG_LOG_LEVEL                   = 8
ARG_WIZ_DATACENTER              = 9
ARG_WRITE_MODE                  = 10

# Pass in runtime variables
client_id                               = sys.argv[ARG_CLIENT_ID]
client_secret                           = sys.argv[ARG_CLIENT_SECRET]
root_project_id                         = sys.argv[ARG_ROOT_PROJECT_ID]
include_archived                        = sys.argv[ARG_INCLUDE_ARCHIVED]
set_project_name_suffix                 = sys.argv[ARG_PROJECT_NAME_SUFFIX]
set_slug_suffix                         = sys.argv[ARG_SLUG_SUFFIX]
set_archive_status                      = sys.argv[ARG_SET_ARCHIVE_STATUS]
log_level                               = sys.argv[ARG_LOG_LEVEL]
wiz_datacenter                          = sys.argv[ARG_WIZ_DATACENTER]
enable_write_mode                       = sys.argv[ARG_WRITE_MODE]

enable_write_mode   = str(enable_write_mode).lower()

if enable_write_mode == "true":
    enable_write_mode = True
elif enable_write_mode == "false":
    enable_write_mode = False

target_archived     = str(include_archived).lower()

if include_archived == "true":
    include_archived = True
elif include_archived == "false":
    include_archived = False

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

def pull_projects(project_id, is_root, include_archived):

    projects = []

    query       = ctwiz.get_qry_all_projects()
    variables   = {}

    if is_root == True:
        variables   = ctwiz.get_qry_vars_parent_project(project_id, is_root, include_archived)
    else:
        # Therefore looking for child projects
        variables   = ctwiz.get_qry_vars_child_projects(project_id, include_archived)

    print("Querying with variables: " + project_id + " - " + str(is_root) + " - " + str(include_archived))
    results     = ctwiz.query_wiz_api(query, variables, wiz_datacenter)

    for result in results["data"]["projects"]["nodes"]:
        this_project_id     = result["id"]
        this_project_name   = result["name"]
        this_project_slug   = result["slug"]
        this_project_is_archived = result["archived"]
        this_project_is_folder = result["isFolder"]
        this_project_child_project_count = result["childProjectCount"]
        this_project_child_projects = []
        
        if this_project_child_project_count > 0:
            is_root = False
            print("Recursing to find projects with parent project id: " + this_project_id)
            this_project_child_projects = pull_projects(this_project_id, is_root, include_archived)

        this_project = {}
        this_project["id"] = this_project_id
        this_project["name"] = this_project_name
        this_project["slug"] = this_project_slug
        this_project["is_archived"] = this_project_is_archived
        this_project["is_folder"] = this_project_is_folder
        this_project["child_projects"] = this_project_child_projects

        projects.append(this_project)

    return projects

def update_project(project_id, current_project_name, project_name_suffix, current_project_slug, project_slug_suffix, current_project_archive_status, target_archive_status):

    new_project_name = current_project_name + project_name_suffix
    new_project_slug = current_project_slug + project_slug_suffix
    logging.info("")
    logging.info("Updating project " + current_project_name + " (project_id: " + project_id + "):")
    logging.info("Current project name: " + current_project_name + " - New project name: " + new_project_name)
    logging.info("Current project slug: " + current_project_slug + " - New project slug: " + new_project_slug)
    logging.info("Current project archived status: is_archived: " + str(current_project_archive_status) + " - New project archived status: is_archived: " + str(target_archive_status))

def loop_and_update_projects(all_projects, project_name_suffix, slug_suffix, target_archive_status):

    for project in all_projects:
        update_project(project["id"], project["name"], project_name_suffix, project["slug"], slug_suffix, project["is_archived"], target_archive_status)
        
        if len(project["child_projects"]) > 0:
            logging.info("Recursing to update projects with parent project id: " + project["id"])
            loop_and_update_projects(project["child_projects"], project_name_suffix, slug_suffix, target_archive_status)

def main():

    set_logging_level(log_level)

    logging.info("Getting token.")
    ctwiz.request_wiz_api_token(client_id, client_secret)

    logging.info("Pulling all projects...")
    # Start off with root
    is_root   = True
    all_projects = pull_projects(root_project_id, is_root, include_archived)

    print(all_projects)

    if enable_write_mode == True:
        print("")
        print("")
        print("Will now update project_id \"" + root_project_id +"\" and all child projects to the following settings:")
        print("Project Name Suffix: " + set_project_name_suffix)
        print("Slug Suffix:" + set_slug_suffix)
        print("Archive Status: " + set_archive_status)
    
        proceed = "None"
        while proceed != "Y" and proceed != "N":
            proceed = input("Happy with the above? Type `Y` or `N`... ")

        if proceed == "Y":
            print("Would now proceed...")
            loop_and_update_projects(all_projects, set_project_name_suffix, set_slug_suffix, set_archive_status)
        if proceed == "N":
            print("Will not proceed.")
            exit(1)

if __name__ == '__main__':
    main()