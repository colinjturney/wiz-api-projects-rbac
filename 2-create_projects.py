# Filename: 2-create_projects.py

# Purpose: Loop through a CSV input file and build a project structure in Wiz as prescribed in that file.

# Python 3.6+
# pip install gql==3.0.0a5 aiohttp==3.7.3
import http.client
import json
import csv
import os
import sys
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

ARG_CLIENT_ID                   = 1
ARG_CLIENT_SECRET               = 2
ARG_INPUT_FILENAME              = 3
ARG_OUTPUT_FILENAME             = 4
ARG_LOG_LEVEL                   = 5
ARG_WIZ_DATACENTER              = 6
ARG_WRITE_MODE                  = 7

# Pass in runtime variables
client_id                               = sys.argv[ARG_CLIENT_ID]
client_secret                           = sys.argv[ARG_CLIENT_SECRET]
input_filename                          = sys.argv[ARG_INPUT_FILENAME]
output_filename                         = sys.argv[ARG_OUTPUT_FILENAME]
log_level                               = sys.argv[ARG_LOG_LEVEL]
wiz_datacenter                          = sys.argv[ARG_WIZ_DATACENTER]
enable_write_mode                       = sys.argv[ARG_WRITE_MODE]

enable_write_mode = str(enable_write_mode).lower()

if enable_write_mode == "true":
    enable_write_mode = True
elif enable_write_mode == "false":
    enable_write_mode = False

api_endpoint = "https://api." + wiz_datacenter + ".app.wiz.io/graphql"
auth_endpoint = "auth.app.wiz.io"

def checkAPIerrors(query, variables, access_token):
    transport = AIOHTTPTransport(
        url=api_endpoint,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    client = Client(transport=transport, fetch_schema_from_transport=False,
                    execute_timeout=55)

    try:
        result = client.execute(query, variable_values=variables)
    except Exception as e:
        if ('502: Bad Gateway' not in str(e)
           and '503: Service Unavailable' not in str(e)):
            print("<p>Wiz-API-Error: %s</p>" % str(e))
            return(e)
        else:
            print("Retry")
    return result

createProject_query = gql("""
  mutation CreateProject($input: CreateProjectInput!) {
      createProject(input: $input) {
        project {
          id
        }
      }
    }
""")

createFolderProject_variables = {
  'input': {
    'name': '',
    'identifiers': [],
    'isFolder': '',
    'description': '',
    'securityChampions': [],
    'projectOwners': [],
    'businessUnit': '',
    'riskProfile': {
      'businessImpact': 'MBI',
      'hasExposedAPI': 'UNKNOWN',
      'hasAuthentication': 'UNKNOWN',
      'isCustomerFacing': 'UNKNOWN',
      'isInternetFacing': 'UNKNOWN',
      'isRegulated': 'UNKNOWN',
      'sensitiveDataTypes': [],
      'storesData': 'UNKNOWN',
      'regulatoryStandards': []
    }
  }
}

createProject_variables = {
  'input': {
    'name': '',
    'identifiers': [],
    'cloudOrganizationLinks': [],
    'cloudAccountLinks': [],
    'repositoryLinks': [],
    'description': '',
    'securityChampions': [],
    'projectOwners': [],
    'businessUnit': '',
    'riskProfile': {
      'businessImpact': 'MBI',
      'hasExposedAPI': 'UNKNOWN',
      'hasAuthentication': 'UNKNOWN',
      'isCustomerFacing': 'UNKNOWN',
      'isInternetFacing': 'UNKNOWN',
      'isRegulated': 'UNKNOWN',
      'sensitiveDataTypes': [],
      'storesData': 'UNKNOWN',
      'regulatoryStandards': []
    }
  }
}

cloudAccount_query = gql("""
  query CloudAccountsPage(
      $filterBy: CloudAccountFilters
      $first: Int
      $after: String
    ) {
      cloudAccounts(filterBy: $filterBy, first: $first, after: $after) {
        nodes {
          id
          name
          externalId
          cloudProvider
        }
      }
    }
""")

cloudAccount_variables = {
  'first': 20,
  'filterBy': {
    'search': [
      ''
    ]
  }
}

cloudOrganization_query = gql("""
  query CloudOrganizations(
      $filterBy: CloudOrganizationFilters
      $first: Int
      $after: String
    ) {
      cloudOrganizations(filterBy: $filterBy, first: $first, after: $after) {
        nodes {
          id
          name
          externalId
          cloudProvider
        }
      }
    }
""")

cloudOrganization_variables = {
  'first': 20,
  'filterBy': {
    'search': [
      ''
    ]
  }
}

def write_to_output_file(project_name, project_id, is_folder):
    
    f = open(output_filename, "a")
    f.write("\"" + project_id + "\",\"" + project_name + "\",\"" + is_folder + "\"\n")


def createProject(access_token, query, variables):
    """Query WIZ API for the given query data schema"""

    result = None

    if enable_write_mode == True:
        result = checkAPIerrors(query, variables, access_token)
    else:
        print("Skipping creation of this project as write mode is disabled.")

    return result

def getCloudObjectDetails(access_token, query, variables):
    """Query WIZ API for the given query data schema"""
    result = checkAPIerrors(query, variables, access_token)

    return result


def getProjectIdFromName(access_token, p_name, is_folder):
    getProjectsquery = gql("""
        query ProjectsTable(
            $filterBy: ProjectFilters
            $first: Int
            $after: String
            $orderBy: ProjectOrder
        ) {
            projects(
            filterBy: $filterBy
            first: $first
            after: $after
            orderBy: $orderBy
            ) {
            nodes {
                id
                name
                cloudAccountLinks{
                    cloudAccount {
                        id
                        externalId
                    }
                    shared
                    environment
                    resourceGroups
                    resourceTags{
                        key
                        value
                    }
                }
                cloudOrganizationLinks{
                    cloudOrganization {
                        id
                        externalId
                    }
                    shared
                    environment
                    resourceGroups
                    resourceTags{
                        key
                        value
                    }
                }
                ancestorProjects {
                    id
                }
                isFolder
            }
            pageInfo {
                hasNextPage
                endCursor
            }
            totalCount
            }
        }
        """)
    
    getProjectsvariables = {
        "first": 1,
        "filterBy": {
            "search": p_name,
            "isFolder": is_folder
        },
        "orderBy": {
            "field": "NAME",
            "direction": "ASC"
        }
    }

    result = checkAPIerrors(getProjectsquery, getProjectsvariables,
                            access_token)

    return result['projects']['nodes'][0]["id"]

def getProjects(access_token, p_name, is_folder):
    getProjectsquery = gql("""
        query ProjectsTable(
            $filterBy: ProjectFilters
            $first: Int
            $after: String
            $orderBy: ProjectOrder
        ) {
            projects(
            filterBy: $filterBy
            first: $first
            after: $after
            orderBy: $orderBy
            ) {
            nodes {
                id
                name
                cloudAccountLinks{
                    cloudAccount {
                        id
                        externalId
                    }
                    shared
                    environment
                    resourceGroups
                    resourceTags{
                        key
                        value
                    }
                }
                cloudOrganizationLinks{
                    cloudOrganization {
                        id
                        externalId
                    }
                    shared
                    environment
                    resourceGroups
                    resourceTags{
                        key
                        value
                    }
                }
                ancestorProjects {
                    id
                }
                isFolder
            }
            pageInfo {
                hasNextPage
                endCursor
            }
            totalCount
            }
        }
        """)
    
    getProjectsvariables = {
        "first": 1,
        "filterBy": {
            "search": p_name,
            "isFolder": is_folder
        },
        "orderBy": {
            "field": "NAME",
            "direction": "ASC"
        }
    }

    result = checkAPIerrors(getProjectsquery, getProjectsvariables,
                            access_token)

    return result['projects']['nodes']

def mutateProject(access_token, p, input, is_cloud_org=False, patch_parent=False):
    query = gql("""
    mutation UpdateProject($input: UpdateProjectInput!) {
        updateProject(input: $input) {
            project {
                id
            }
        }
        }
    """)

    variables = {
        'input': {
            'id': p,
            'patch': {
            }
        }
    }

    if patch_parent:
        variables['input']['patch']['parentProjectId'] = input
    elif is_cloud_org:
        variables['input']['patch']['cloudOrganizationLinks'] = input
    else:
        variables['input']['patch']['cloudAccountLinks'] = input

    result = None

    if enable_write_mode == True:
        result = checkAPIerrors(query, variables, access_token)
    else:
        print("Skipping creation of this project as write mode is disabled.")




    return result

def request_wiz_api_token(client_id, client_secret):
    """Retrieve an OAuth access token to be used against Wiz API"""
    headers = {
        "content-type": "application/x-www-form-urlencoded"
    }
    payload = (f"grant_type=client_credentials&client_id={client_id}"
               f"&client_secret={client_secret}&audience=wiz-api")

    conn = http.client.HTTPSConnection(auth_endpoint)
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    token_str = res.read().decode("utf-8")

    return json.loads(token_str)["access_token"]

def ask_user(raw_input):
    check = str(raw_input).lower().strip()
    try:
        if check[0] == 'y' or check[0] == 'yes':
            return True
        elif check[0] == 'n' or check[0] == 'no':
            return False
        else:
            print('Invalid Input. \nCan we continue using the same Projects',
                  'if they exist already?')
            return ask_user(input())
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return ask_user(input())

# ===== MAIN =======

if __name__ == "__main__":
    print("Create token...")
    token = request_wiz_api_token(client_id, client_secret)

    print("Initialising output file...")
    f = open(output_filename,"w")
    f.write("Project ID, Project Name, Is Folder\n")

    print("\nReading the input file, so we can walk through",
        "it and create Projects.")
    with open(input_filename, newline='') as f:
        # Reading and ignoring the first line as it has the CSV headers...
        f.readline()
        reader = csv.reader(f, delimiter=',')
        projects_input_from_file = list(reader)

    print("\nStart to create Projects with the associated",
        "Subscriptions, Cloud Organizations, and Parent Folders"
        " from the input file\n")

    print(f"Inputs:\n")
    print(f"wiz_project_name, isFolder, cloudAccountLinks, cloudOrganizationLinks, parentProjectName, projectId")
    for line in projects_input_from_file:
        print(f"{line}")
    print("\n")

    print("Can we continue updating Projects if they already exist?")
    confirm_projects_method = ask_user(input())
    if not confirm_projects_method:
        print("Per user input, not updating existing Projects, but rather",
            "only creating new Projects and skipping existing ones.")
        update_existing_projects = False
    else:
        print("Per user input, we\'ll also update existing Projects.")
        update_existing_projects = True

    for project in projects_input_from_file:

        isFolder = False
        if project[1].lower() == "true":
            isFolder = True

        print("########################")
        print(f"Validating if Project with name \"{project[0]}\" exists.")
        project_list = getProjects(token, project[0], isFolder)

        cal = []
        col = []
        if not project_list:

            print(f"Creating Project \"{project[0]}\" with",
                f"\nisFolder: [{project[1]}]", 
                f"\naccounts: [{project[2]}]", 
                f"\ncloud organizations:[{project[3]}]"
                f"\nparent folder name: \"{project[4]}\" \n")

            accounts = project[2].split(",") if len(project[2]) > 0 else []
            for account in accounts:

                # fetch Wiz GUID of the subscription ID from the input
                cloudAccount_variables['filterBy']['search'] = [account]
                wiz_account_id = getCloudObjectDetails(token, cloudAccount_query,
                                                        cloudAccount_variables)

                if wiz_account_id['cloudAccounts']['nodes']:
                    cal.append({'cloudAccount': wiz_account_id['cloudAccounts']['nodes'][0]['id'],  # noqa: 501
                                'environment': 'PRODUCTION', 'shared': False})
                else:
                    print(f">>>>>>> Account {account} doesn\'t exist in Wiz yet.",
                        "Skipping adding it to the computed list. Please check",
                        "and rectify later! <<<<<<<\n")
        
            orgs = project[3].split(",") if len(project[3]) > 0 else []
            for org in orgs:

                # fetch Wiz GUID of the subscription ID from the input
                cloudOrganization_variables['filterBy']['search'] = [org]
                wiz_org_id = getCloudObjectDetails(token, cloudOrganization_query,
                                                        cloudOrganization_variables)

                if wiz_org_id['cloudOrganizations']['nodes']:
                    col.append({'cloudOrganization': wiz_org_id['cloudOrganizations']['nodes'][0]['id'],  # noqa: 501
                                'environment': 'PRODUCTION', 'shared': False})
                else:
                    print(f">>>>>>> Account {account} doesn\'t exist in Wiz yet.",
                        "Skipping adding it to the computed list. Please check",
                        "and rectify later! <<<<<<<\n")
                    
            createProject_response = None

            isFolder = None

            if project[1].lower() == "true":
                isFolder = True
            elif project[1].lower() == "false":
                isFolder = False

            parentProjectId = None
                
            if len(project[4]) > 0:
                # Parent Project ID must be a folder, so hardcoding True here
                parentProjectId = getProjectIdFromName(token, project[4], True)
                print(f"\nfound parent project id: \"" + parentProjectId + "\" \n")

            # If this is a folder project
            if isFolder == True:

                createFolderProject_variables['input']['name'] = project[0]
                createFolderProject_variables['input']['isFolder'] = isFolder
                createFolderProject_variables['input']['parentProjectId'] = parentProjectId if parentProjectId else None
                createProject_response = createProject(token, createProject_query,
                                                    createFolderProject_variables)
            
            elif isFolder == False:

                createProject_variables['input']['name'] = project[0]
                createProject_variables['input']['isFolder'] = isFolder
                createProject_variables['input']['cloudAccountLinks'] = cal
                createProject_variables['input']['cloudOrganizationLinks'] = col
                createProject_variables['input']['parentProjectId'] = parentProjectId if parentProjectId else None
                createProject_response = createProject(token, createProject_query,
                                                    createProject_variables)


            print(f"Created Project \"{project[0]}\". Successful creation output",
            f" and Project ID:\n{createProject_response}")

            projectId = createProject_response["createProject"]["project"]["id"]

            write_to_output_file(project[0], projectId, project[1])
            
            print("\nConsider editing the newly created project and tweaking its",
            "settings.\ne.g., description, risk profiile, regulatory",
            "standards, etc.")

        else:
            # if projects_list has more than one entry, we had multiple hits on the search name. I couldn't find
            # a means to filter this in the query, so we'll post process to ensure we're acting on the project with 
            # the exact same name. Multiple projects with the same names will cause issues

            if project_list and len(project_list) > 1:
                temp = []
                for p in project_list:
                    if p['name'] == project[0]:
                        temp.append(p)
                        break
                project_list = temp

            print("\nProject exists.")
            if update_existing_projects:
                print("Based on your acknowledgement in the beginning of this",
                    f"script,\nUpdating Project \"{project[0]}\" with",
                    f"\nis folder:[{project[1]}]"
                    f"\naccounts: [{project[2]}]", 
                    f"\ncloud organizations:[{project[3]}]"
                    f"\nparent folder name association: \"{project[4]}\" \n")

                current_project_cal = project_list[0]['cloudAccountLinks']
                current_project_col = project_list[0]['cloudOrganizationLinks']
                current_project_ancestors = project_list[0]['ancestorProjects'] if project_list[0]['ancestorProjects'] else None

                # hack to fix output of ['cloudAccount]['cloudAccount'] to
                # input of ['cloudAccount']
                cal = current_project_cal
                for item_current, item_new in zip(current_project_cal, cal):
                    item_new['cloudAccount'] = item_current['cloudAccount']['id']
                accounts = project[2].split(",") if len(project[2]) > 0 else []

                apply_mutation = False
                for account in accounts:

                    account_already_in_cal = False
                    # fetch Wiz GUID of the subscription ID from the input
                    cloudAccount_variables['filterBy']['search'] = [account]
                    wiz_account_id = getCloudObjectDetails(token,
                                                            cloudAccount_query,
                                                            cloudAccount_variables)

                    if wiz_account_id['cloudAccounts']['nodes']:
                        for item in cal:
                            if item['cloudAccount'] == wiz_account_id['cloudAccounts']['nodes'][0]['id']:  # noqa: 501
                                account_already_in_cal = True
                                break
                            else:
                                account_already_in_cal = False

                        if not account_already_in_cal:
                            cal.append({'cloudAccount': wiz_account_id['cloudAccounts']['nodes'][0]['id'],  # noqa: 501
                                        'environment': 'PRODUCTION',
                                        'shared': False})
                            apply_mutation = True
                    else:
                        print(f">>>>>>> Account {account} doesn\'t exist",
                            "in Wiz yet.",
                            "Skipping adding it to the computed list.",
                            "Please check and rectify later! <<<<<<<\n")
                
                if apply_mutation:
                    mutateProject(token, project_list[0]['id'], cal, is_cloud_org=False)
                    print(f">>>>>>> Updated CloudAccountLinks applied.")
                else:
                    print(f">>>>>>> No changes to CloudAccountLinks to apply")

                # --------------------------------------------------------------

                apply_mutation = False
                col = current_project_col
                for item_current, item_new in zip(current_project_col, col):
                    item_new['cloudOrganization'] = item_current['cloudOrganization']['id']
                orgs = project[3].split(",") if len(project[3]) > 0 else []

                for org in orgs:
                    account_already_in_col = False
                    # fetch Wiz GUID of the subscription ID from the input
                    cloudOrganization_variables['filterBy']['search'] = [org]
                    wiz_account_id = getCloudObjectDetails(token,
                                                            cloudOrganization_query,
                                                            cloudOrganization_variables)

                    if wiz_account_id['cloudOrganizations']['nodes']:
                        for item in col:
                            if item['cloudOrganization'] == wiz_account_id['cloudOrganizations']['nodes'][0]['id']:  # noqa: 501
                                account_already_in_col = True
                                break
                            else:
                                account_already_in_col = False

                        if not account_already_in_col:
                            col.append({'cloudOrganization': wiz_account_id['cloudOrganizations']['nodes'][0]['id'],  # noqa: 501
                                        'environment': 'PRODUCTION',
                                        'shared': False})
                            apply_mutation = True

                    else:
                        print(f">>>>>>> Cloud Organization {org} doesn\'t exist",
                            "in Wiz yet.",
                            "Skipping adding it to the computed list.",
                            "Please check and rectify later! <<<<<<<\n")

                if apply_mutation:
                    mutateProject(token, project_list[0]['id'], col, is_cloud_org=True)
                    print(f">>>>>>> Updated CloudOrganizationLinks applied.")
                else:
                    print(f">>>>>>> No changes to CloudOrganizationLinks to apply")

                # --------------------------------------------------------------

                ## Update parent project if needed
                apply_mutation = False
                current_project_ancestor = None

                parentProjectId = None
                
                if len(project[4]) > 0:
                    # Parent Project ID must be a folder, so hardcoding True here
                    parentProjectId = getProjectIdFromName(token, project[4], True)
                    print(f"\nfound parent project id: \"" + parentProjectId + "\" \n")

                if current_project_ancestors and len(current_project_ancestors) > 1:
                    found_ancestor = False
                    for ancestor in current_project_ancestors:
                        if ancestor == parentProjectId:
                            found_ancestor = True
                            print(f">>>>>>> No change to parentProject to apply") 
                            break

                    if not found_ancestor:
                        # if we go through the ancestors and don't have a match on parents, we need to update
                        apply_mutation = True
                else:
                    current_project_ancestor = current_project_ancestors[0]['id'] if current_project_ancestors else None
                    if str(current_project_ancestor or '') != parentProjectId:
                        apply_mutation = True

                if apply_mutation:
                    # update parent project
                    mutateProject(token, project_list[0]['id'], parentProjectId, is_cloud_org=False, patch_parent=True)
                    print(f">>>>>>> Updated parentProject applied.")
                else:
                    print(f">>>>>>> No changes to parentProject applied.")

                write_to_output_file(project_list[0]["name"], project_list[0]["id"], str(project_list[0]["isFolder"]))


            else:
                print(f"Not updating Project \"{project[0]}\",",
                    "based on your acknowledgement in the beginning",
                    "of this script.")