# Filename: create_projects_csv.py

# Purpose: Loop through all Azure Management Groups that are children of a defined management group and create folder projects for them.
#          Note: Top-level management groups will have folder projects created prepended with Azure-

import requests
import json
import sys
import ctwiz
import logging
import csv

ARG_ADGROUPS_INPUT_FILE         = 1
ARG_SAML_MAPPINGS_OUTPUT_FILE   = 2
ARG_DEFAULT_SAML_ROLE           = 3
ARG_LOG_LEVEL                   = 4

# Pass in runtime variables
adgroups_input_file         = sys.argv[ARG_ADGROUPS_INPUT_FILE]
saml_mappings_output_file   = sys.argv[ARG_SAML_MAPPINGS_OUTPUT_FILE]
default_saml_role           = sys.argv[ARG_DEFAULT_SAML_ROLE]
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

def initialise_output_file():
    g = open(saml_mappings_output_file,"w")
    g.write("SAML Group Name,Permissions,Project Name\n")


def build_saml_groupings_array(default_saml_role):

    saml_mappings = {}
    print("\nReading the ad groups input file, so we can walk through",
        "it and build the SAML role mappings.")
    with open(adgroups_input_file, newline='') as f:

        # Reading and ignoring the first line as it has the CSV headers...
        f.readline()
        reader = csv.reader(f, delimiter=',')
        adgroups_input_from_file = list(reader)

    print("\nStarting to build AD groupings with associated project names from input files\n")

    for admapping in adgroups_input_from_file:
        print(f"{admapping}")
        print("\n")

        if admapping[0] not in saml_mappings.keys():
            this_mapping = {}
            this_mapping["group_id"] = admapping[0]
            this_mapping["role"] = default_saml_role
            this_mapping["originating_cloud"] = admapping[4]
            this_mapping["projects"] = {}

            this_mapping["projects"] = {}

            this_project = {}

            this_project["users"] = {}

            this_user = {}
            this_user["membername"] = admapping[2]
            this_user["memberupn"]  = admapping[3] 

            this_project["users"] = this_user

            this_mapping["projects"][admapping[1]] = this_project

            saml_mappings[admapping[0]] = this_mapping

        # If AD Mapping already exists
        elif admapping[0] in saml_mappings.keys():

            # If this project does not yet exist in this AD mapping
            if admapping[1] not in saml_mappings[admapping[0]]["projects"].keys():

                this_project = {}
                
                this_project["users"] = {}

                this_user = {}
                this_user["membername"] = admapping[2]
                this_user["memberupn"]  = admapping[3] 

                this_project["users"][admapping[3]] = this_user

                saml_mappings[admapping[0]]["projects"][admapping[1]] = this_project

            # If this project does exist, then does this user exist?
            elif admapping[1] in saml_mappings[admapping[0]]["projects"].keys():

                if admapping[3] not in saml_mappings[admapping[0]]["projects"][admapping[1]]["users"].keys():

                    this_user = {}
                    this_user["membername"] = admapping[2]
                    this_user["memberupn"]  = admapping[3] 

                    this_project["users"][admapping[3]] = this_user

                    saml_mappings[admapping[0]]["projects"][admapping[1]] = this_project
                else:
                    print("Spotted duplicate mapping")
    
    return saml_mappings
            
def write_mappings_to_output_file(saml_mappings, default_saml_role):

    f = open(saml_mappings_output_file, "a")

    for group_name in saml_mappings.keys():

        project_list = saml_mappings[group_name]["projects"].keys()

        f.write("\"" + group_name + "\",\"" + default_saml_role + "\",\"" + ','.join(project_list) + "\"\n")

def main():

    set_logging_level(log_level)

    logging.info("Initialising Output File...")
    initialise_output_file()

    logging.info("Modelling AD group structure...")
    saml_mappings = build_saml_groupings_array(default_saml_role)

    logging.info("Writing to output file...")
    write_mappings_to_output_file(saml_mappings, default_saml_role)

if __name__ == '__main__':
    main()