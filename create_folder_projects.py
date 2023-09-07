# Filename: create_folder_projects.py
# Purpose: Loop through all Azure Management Groups that are children of a defined management group and create folder projects for them.
#          Note: Top-level management groups will have folder projects created prepended with Azure-

import requests
import json
import sys

# Standard headers
HEADERS_AUTH = {"Content-Type": "application/x-www-form-urlencoded"}
HEADERS = {"Content-Type": "application/json"}

# Expect Wiz client_id, client_secret, root_management_group_id and default_user_role to be passed in as runtime variables.
client_id = sys.argv[1]
client_secret = sys.argv[2]

# Where to run the query from- i.e. the root management group id.
root_management_group_id = sys.argv[3]

# The default Wiz RBAC role to assign to users. Should be project scoped.
default_user_role = sys.argv[4]

# Uncomment the following section to define the proxies in your environment,
#   if necessary:
# http_proxy  = "http://"+user+":"+passw+"@x.x.x.x:abcd"
# https_proxy = "https://"+user+":"+passw+"@y.y.y.y:abcd"
# proxyDict = {
#     "http"  : http_proxy,
#     "https" : https_proxy
# }

def query_wiz_api(query, variables):
    """Query Wiz API for the given query data schema"""
    data = {"variables": variables, "query": query}

    try:
        # Uncomment the next first line and comment the line after that
        # to run behind proxies
        # result = requests.post(url="https://api.us20.app.wiz.io/graphql",
        #                        json=data, headers=HEADERS, proxies=proxyDict)
        result = requests.post(url="https://api.us20.app.wiz.io/graphql",
                               json=data, headers=HEADERS)

    except Exception as e:
        if ('502: Bad Gateway' not in str(e) and
                '503: Service Unavailable' not in str(e) and
                '504: Gateway Timeout' not in str(e)):
            print("<p>Wiz-API-Error: %s</p>" % str(e))
            return(e)
        else:
            print("Retry")

    return result.json()


def request_wiz_api_token(client_id, client_secret):
    """Retrieve an OAuth access token to be used against Wiz API"""
    auth_payload = {
      'grant_type': 'client_credentials',
      'audience': 'wiz-api',
      'client_id': client_id,
      'client_secret': client_secret
    }
    # Uncomment the next first line and comment the line after that
    # to run behind proxies
    # response = requests.post(url="https://auth.app.wiz.io/oauth/token",
    #                         headers=HEADERS_AUTH, data=auth_payload,
    #                         proxies=proxyDict)
    response = requests.post(url="https://auth.app.wiz.io/oauth/token",
                             headers=HEADERS_AUTH, data=auth_payload)

    if response.status_code != requests.codes.ok:
        raise Exception('Error authenticating to Wiz [%d] - %s' %
                        (response.status_code, response.text))

    try:
        response_json = response.json()
        TOKEN = response_json.get('access_token')
        if not TOKEN:
            message = 'Could not retrieve token from Wiz: {}'.format(
                    response_json.get("message"))
            raise Exception(message)
    except ValueError as exception:
        print(exception)
        raise Exception('Could not parse API response')
    HEADERS["Authorization"] = "Bearer " + TOKEN

    return TOKEN

def get_role_bindings(subscription_id):
    query = ("""
        query GraphSearch(
            $query: GraphEntityQueryInput
            $controlId: ID
            $projectId: String!
            $first: Int
            $after: String
            $fetchTotalCount: Boolean!
            $quick: Boolean = true
            $fetchPublicExposurePaths: Boolean = false
            $fetchInternalExposurePaths: Boolean = false
            $fetchIssueAnalytics: Boolean = false
            $fetchLateralMovement: Boolean = false
            $fetchKubernetes: Boolean = false
        ) {
            graphSearch(
            query: $query
            controlId: $controlId
            projectId: $projectId
            first: $first
            after: $after
            quick: $quick
            ) {
            totalCount @include(if: $fetchTotalCount)
            maxCountReached @include(if: $fetchTotalCount)
            pageInfo {
                endCursor
                hasNextPage
            }
            nodes {
                entities {
                ...PathGraphEntityFragment
                userMetadata {
                    isInWatchlist
                    isIgnored
                    note
                }
                technologies {
                    id
                    icon
                }
                publicExposures(first: 10) @include(if: $fetchPublicExposurePaths) {
                    nodes {
                    ...NetworkExposureFragment
                    }
                }
                otherSubscriptionExposures(first: 10)
                    @include(if: $fetchInternalExposurePaths) {
                    nodes {
                    ...NetworkExposureFragment
                    }
                }
                otherVnetExposures(first: 10)
                    @include(if: $fetchInternalExposurePaths) {
                    nodes {
                    ...NetworkExposureFragment
                    }
                }
                lateralMovementPaths(first: 10) @include(if: $fetchLateralMovement) {
                    nodes {
                    id
                    pathEntities {
                        entity {
                        ...PathGraphEntityFragment
                        }
                    }
                    }
                }
                kubernetesPaths(first: 10) @include(if: $fetchKubernetes) {
                    nodes {
                    id
                    path {
                        ...PathGraphEntityFragment
                    }
                    }
                }
                }
                aggregateCount
            }
            }
        }
    
        fragment PathGraphEntityFragment on GraphEntity {
            id
            name
            type
            properties
            issueAnalytics: issues(filterBy: { status: [IN_PROGRESS, OPEN] })
            @include(if: $fetchIssueAnalytics) {
            highSeverityCount
            criticalSeverityCount
            }
        }

    
        fragment NetworkExposureFragment on NetworkExposure {
            id
            portRange
            sourceIpRange
            destinationIpRange
            path {
            ...PathGraphEntityFragment
            }
            applicationEndpoints {
            ...PathGraphEntityFragment
            }
        }
    """)

    # The variables sent along with the above query
    variables = {
        "quick": True,
        "fetchPublicExposurePaths": True,
        "fetchInternalExposurePaths": False,
        "fetchIssueAnalytics": False,
        "fetchLateralMovement": True,
        "fetchKubernetes": False,
        "first": 50,
        "query": {
            "type": [
            "SUBSCRIPTION"
            ],
            "select": True,
            "where": {
                "cloudPlatform": {
                    "EQUALS": [
                    "Azure"
                    ]
                },
                "subscriptionId": {
                    "EQUALS": [
                        "93e2fb4e-e46a-4ee5-8be0-1a4f555eb1ff"
                    ]
                }
            },
            "relationships": [
            {
                "type": [
                {
                    "type": "APPLIES_TO",
                    "reverse": True
                }
                ],
                "with": {
                "type": [
                    "ACCESS_ROLE_BINDING"
                ],
                "select": True,
                "relationships": [
                    {
                    "type": [
                        {
                        "type": "ASSIGNED_TO"
                        }
                    ],
                    "with": {
                        "type": [
                        "USER_ACCOUNT"
                        ],
                        "select": True
                    }
                    }
                ]
                }
            }
            ]
        },
        "projectId": "*",
        "fetchTotalCount": False
    }

    results = query_wiz_api(query, variables)

    # Adding to dict to ensure duplicate results won't be added. Need to add logic to catch any related errors here.

    role_bindings = {}

    for result in results["data"]["graphSearch"]["nodes"]:

        entities = result["entities"]

        if entities[2] != None:
            role_bindings[entities[2]["properties"]["otherMails"]] = {
                "display_name" : entities[2]["properties"]["displayName"],
                "email_address"  : entities[2]["properties"]["otherMails"]
            }

    return role_bindings


def model_project_structure():

    query = ("""
        query GraphSearch(
            $query: GraphEntityQueryInput
            $controlId: ID
            $projectId: String!
            $first: Int
            $after: String
            $fetchTotalCount: Boolean!
            $quick: Boolean = true
            $fetchPublicExposurePaths: Boolean = false
            $fetchInternalExposurePaths: Boolean = false
            $fetchIssueAnalytics: Boolean = false
            $fetchLateralMovement: Boolean = false
            $fetchKubernetes: Boolean = false
        ) {
            graphSearch(
            query: $query
            controlId: $controlId
            projectId: $projectId
            first: $first
            after: $after
            quick: $quick
            ) {
            totalCount @include(if: $fetchTotalCount)
            maxCountReached @include(if: $fetchTotalCount)
            pageInfo {
                endCursor
                hasNextPage
            }
            nodes {
                entities {
                ...PathGraphEntityFragment
                userMetadata {
                    isInWatchlist
                    isIgnored
                    note
                }
                technologies {
                    id
                    icon
                }
                publicExposures(first: 10) @include(if: $fetchPublicExposurePaths) {
                    nodes {
                    ...NetworkExposureFragment
                    }
                }
                otherSubscriptionExposures(first: 10)
                    @include(if: $fetchInternalExposurePaths) {
                    nodes {
                    ...NetworkExposureFragment
                    }
                }
                otherVnetExposures(first: 10)
                    @include(if: $fetchInternalExposurePaths) {
                    nodes {
                    ...NetworkExposureFragment
                    }
                }
                lateralMovementPaths(first: 10) @include(if: $fetchLateralMovement) {
                    nodes {
                    id
                    pathEntities {
                        entity {
                        ...PathGraphEntityFragment
                        }
                    }
                    }
                }
                kubernetesPaths(first: 10) @include(if: $fetchKubernetes) {
                    nodes {
                    id
                    path {
                        ...PathGraphEntityFragment
                    }
                    }
                }
                }
                aggregateCount
            }
            }
        }
    
        fragment PathGraphEntityFragment on GraphEntity {
            id
            name
            type
            properties
            issueAnalytics: issues(filterBy: { status: [IN_PROGRESS, OPEN] })
            @include(if: $fetchIssueAnalytics) {
            highSeverityCount
            criticalSeverityCount
            }
        }

    
        fragment NetworkExposureFragment on NetworkExposure {
            id
            portRange
            sourceIpRange
            destinationIpRange
            path {
            ...PathGraphEntityFragment
            }
            applicationEndpoints {
            ...PathGraphEntityFragment
            }
        }
    """)

    variables = {
        "quick": True,
        "fetchPublicExposurePaths": True,
        "fetchInternalExposurePaths": False,
        "fetchIssueAnalytics": False,
        "fetchLateralMovement": True,
        "fetchKubernetes": False,
        "first": 50,
        "query": {
            "type": [
            "CLOUD_ORGANIZATION"
            ],
            "select": True,
            "where": {
            "externalId": {
                "EQUALS": [
                root_management_group_id
                ]
            }
            },
            "relationships": [
            {
                "type": [
                {
                    "type": "CONTAINS"
                }
                ],
                "with": {
                "type": [
                    "CLOUD_ORGANIZATION"
                ],
                "select": True,
                "relationships": [
                    {
                    "type": [
                        {
                        "type": "CONTAINS"
                        }
                    ],
                    "optional": True,
                    "with": {
                        "type": [
                        "SUBSCRIPTION"
                        ],
                        "select": True
                    }
                    },
                    {
                    "type": [
                        {
                        "type": "CONTAINS"
                        }
                    ],
                    "optional": True,
                    "with": {
                        "type": [
                        "CLOUD_ORGANIZATION"
                        ],
                        "select": True,
                        "relationships": [
                        {
                            "type": [
                            {
                                "type": "CONTAINS"
                            }
                            ],
                            "with": {
                            "type": [
                                "SUBSCRIPTION"
                            ],
                            "select": True
                            },
                            "optional": True
                        }
                        ]
                    }
                    }
                ]
                }
            },
            {
                "type": [
                {
                    "type": "CONTAINS"
                }
                ],
                "optional": True,
                "with": {
                "type": [
                    "SUBSCRIPTION"
                ],
                "select": True
                }
            }
            ]
        },
        "projectId": "*",
        "fetchTotalCount": False
    }

    results = query_wiz_api(query, variables)
    structure = {}

    for result in results["data"]["graphSearch"]["nodes"]:
        entities = result["entities"]


        # Some rows returned are empty if there is no matching entity at the level of the graph, so we'll ignore these if = None.
        if entities[0] != None:

            #entity0: tenant root group

            element                     = {}
            element["folder-projects"]  = {}
            element["projects"]         = {}
            element["project_id"]       = None

            if entities[0]["name"] not in structure.keys():
                structure[entities[0]["name"]] = element

            #entity1: cloud organization - member of entity0 tenant root group

            element                     = {}
            element["folder-projects"]  = {}
            element["projects"]         = {}
            element["project_id"]       = None

            if entities[1]["name"] not in structure[entities[0]["name"]]["folder-projects"].keys():
                structure[entities[0]["name"]]["folder-projects"][entities[1]["name"]] = element

            #entity2: subscription - member of entity1 cloud org
            
            if entities[2] != None:
                element     = {}
                element["users"] = get_role_bindings(entities[2]["properties"]["subscriptionExternalId"])
                element["project_id"] = None
                structure[entities[0]["name"]]["folder-projects"][entities[1]["name"]]["projects"][entities[2]["name"]] = element

            #entity3: cloud organization - member of entity1 cloud org

            if entities[3] != None:
                if entities[3]["name"] not in structure[entities[0]["name"]]["folder-projects"][entities[1]["name"]]["folder-projects"]:
                    element                     = {}
                    element["folder-projects"]  = {}
                    element["projects"]         = {}
                    element["project_id"]       = None
                    structure[entities[0]["name"]]["folder-projects"][entities[1]["name"]]["folder-projects"][entities[3]["name"]] = element

            #entity4: subscription - member of entity3 cloud org

            if entities[4] != None:
                element     = {}
                element["users"] = get_role_bindings(entities[4]["properties"]["subscriptionExternalId"])
                element["project_id"] = None
                structure[entities[0]["name"]]["folder-projects"][entities[1]["name"]]["folder-projects"][entities[3]["name"]]["projects"][entities[4]["name"]] = element
                    
            #entity5: subscription - member of tenant root management group

            if entities[5] != None:
                element     = {}
                element["users"] = get_role_bindings(entities[5]["properties"]["subscriptionExternalId"])
                element["project_id"] = None
                structure[entities[0]["name"]]["projects"][(entities[5]["name"])] = element
    

    return structure



# create_project_structure(structure)
# Creates the project structure and calls provision user function to provision users within each project.

def create_project_structure(structure):

    print(structure)
    print()
    print()

    # Process level 1 folder projects
    for l1fp in structure:
        print("Creating folder project: " + l1fp)
        structure[l1fp]["project_id"] = mock_create_project(l1fp, l1fp, True, None)
        print()

        # Process child projects of level 1 folder projects
        print(" Processing child projects of " + l1fp + "...")
        if structure[l1fp]["projects"] == None:
            print("- None found.")
        for l1_project_name in structure[l1fp]["projects"]:
            project = structure[l1fp]["projects"][l1_project_name]
            print(structure[l1fp]["projects"][l1_project_name])
            print()
            print("  * Creating project: " + l1fp + "/" + l1_project_name)
            structure[l1fp]["projects"][l1_project_name]["project_id"] = mock_create_project(l1_project_name, l1fp + "/" + l1_project_name, False, structure[l1fp]["project_id"])

            if len(project["users"].keys()) > 0:
                users = project["users"]
                for user_name in users:
                    mock_provision_user(users[user_name]["display_name"], users[user_name]["email_address"], "AzureAD", default_user_role, l1fp + "/" + l1_project_name, structure[l1fp]["projects"][l1_project_name]["project_id"])
                    print("        " + users[user_name]["display_name"] + "(" + users[user_name]["email_address"] + "): " + default_user_role + " on " + l1fp + "/" + l1_project_name)
                
        # Process child folder projects of level 1 folder projects
        print()
        print(" Processing child folder projects of " + l1fp + "...")
        for l2fp in structure[l1fp]["folder-projects"]:
            print()
            print("  * Creating folder project: " + l1fp + "/" + l2fp + "...")
            structure[l1fp]["folder-projects"][l2fp]["project_id"] = mock_create_project(l2fp, l1fp + "/" + l2fp, True, structure[l1fp]["project_id"])

            # Process child projects of level 2 folder projects
            print()
            print("    Processing child projects of " + l1fp + "/" + l2fp + "...")
            if len(structure[l1fp]["folder-projects"][l2fp]["projects"]) == 0:
                print("     - None found.")
            for l2_project_name in structure[l1fp]["folder-projects"][l2fp]["projects"]:
                project = structure[l1fp]["folder-projects"][l2fp]["projects"][l2_project_name]
                print("     * Creating project: " + l2_project_name)
                structure[l1fp]["folder-projects"][l2fp]["projects"][l2_project_name]["project_id"] = mock_create_project(l2_project_name, l1fp + "/" + l2fp + "/" + l2_project_name, False, structure[l1fp]["folder-projects"][l2fp]["project_id"])
                if len(project["users"].keys()) > 0:
                    users = project["users"]
                    for user_name in users:
                        mock_provision_user(users[user_name]["display_name"], users[user_name]["email_address"], "AzureAD", default_user_role, l1fp + "/" + l2fp + "/" + l2_project_name,structure[l1fp]["folder-projects"][l2fp]["project_id"])
                        print("        " + users[user_name]["display_name"] + "(" + users[user_name]["email_address"] + "): " + default_user_role + " on " + l1fp + "/" + l2fp + "/" + l2_project_name)

            print()

            # Process child folder projects of level 2 folder projects
            print("    Processing child folder projects of " + l1fp + "/" + l2fp + "...")
            if len(structure[l1fp]["folder-projects"][l2fp]["folder-projects"]) == 0:
                print("     - None found.")
            for l3fp in structure[l1fp]["folder-projects"][l2fp]["folder-projects"]:
                print()
                print("     * Creating folder project " + l1fp + "/" + l2fp + "/" + l3fp)
                structure[l1fp]["folder-projects"][l2fp]["folder-projects"][l3fp]["project_id"] = mock_create_project(l3fp, l1fp + "/" + l2fp + "/" + l3fp, True, structure[l1fp]["folder-projects"][l2fp]["project_id"])
                
                # Process child projects of level 3 folder projects
                print()
                print("       Processing child projects of " + l1fp + "/" + l2fp + "/" + l3fp +  "...")
                for l3_project_name in structure[l1fp]["folder-projects"][l2fp]["folder-projects"][l3fp]["projects"]:
                    project = structure[l1fp]["folder-projects"][l2fp]["folder-projects"][l3fp]["projects"][l3_project_name]
                    print("        * Creating project: " + l3_project_name)
                    structure[l1fp]["folder-projects"][l2fp]["folder-projects"][l3fp]["projects"][l3_project_name]["project_id"] = mock_create_project(l3_project_name,l1fp + "/" + l2fp + "/" + l3fp + "/" + l3_project_name, False, structure[l1fp]["folder-projects"][l2fp]["folder-projects"][l3fp]["project_id"])
                    if len(project["users"].keys()) > 0:
                        users = project["users"]
                        for user_name in users:
                            mock_provision_user(users[user_name]["display_name"], users[user_name]["email_address"], "AzureAD", default_user_role, l1fp + "/" + l2fp + "/" + l3fp + "/" + l3_project_name,structure[l1fp]["folder-projects"][l2fp]["folder-projects"][l3fp]["projects"][l3_project_name]["project_id"])
                            print("           " + users[user_name]["display_name"] + "(" + users[user_name]["email_address"] + "): " + default_user_role + " on " + l1fp + "/" + l2fp + "/" + l3fp + "/" + l3_project_name)
                print()

                # Process child folder projects of level 3 folder projects
                # for l4fp in structure[l1fp]["folder-projects"][l2fp]["folder-projects"][l3fp]["folder-projects"]:
                #     print("creating folder project " + l1fp + "/" + l2fp + "/" + l3fp + "/" + l4fp)
                #     mock_create_project(l1fp + "/" + l2fp + "/" + l3fp + "/" + l4fp + "/")
    print(structure)

# TODO
# create_project(project_name, is_folder, parent_folder_project_id)
# Creates the project in Wiz by calling the Wiz API.
def create_project(project_name, is_folder, parent_folder_project_id):
    query = ("""
        mutation CreateProject($input: CreateProjectInput!) {
            createProject(input: $input) {
            project {
                id
            }
            }
        }
    """)

    variables = {
    "input": {
        "name": project_name,
        "identifiers": [],
        "isFolder": is_folder,
        "description": "",
        "businessUnit": "",
        "riskProfile": {
        "businessImpact": "MBI",
        "hasExposedAPI": "UNKNOWN",
        "hasAuthentication": "UNKNOWN",
        "isCustomerFacing": "UNKNOWN",
        "isInternetFacing": "UNKNOWN",
        "isRegulated": "UNKNOWN",
        "sensitiveDataTypes": [],
        "storesData": "UNKNOWN",
        "regulatoryStandards": []
        },
        "parentProjectId": parent_folder_project_id
    }
    }

# TODO
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

# TODO
# mock_create_project(project_path)
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

#    print("Getting token.")
    request_wiz_api_token(client_id, client_secret)

    initialise_mock_files()
    
    project_structure = model_project_structure()

    create_project_structure(project_structure)

    # The above code lists the first <x> items.
    # If paginating on a Graph Query,
    #   then use <'quick': False> in the query variables.
    # Uncomment the following section to paginate over all the results:
    # pageInfo = result['data']['graphSearch']['pageInfo']
    # while (pageInfo['hasNextPage']):
    #     # fetch next page
    #     variables['after'] = pageInfo['endCursor']
    #     result = query_wiz_api(query, variables)
    #     print(result)
    #     pageInfo = result['data']['graphSearch']['pageInfo']


if __name__ == '__main__':
    main()