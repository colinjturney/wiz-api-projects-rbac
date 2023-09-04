# Filename: create_folder_projects.py
# Purpose: Loop through all Azure Management Groups that are children of a defined management group and create folder projects for them.
#          Note: Top-level management groups will have folder projects created prepended with Azure-

import requests
import json
import sys

# Standard headers
HEADERS_AUTH = {"Content-Type": "application/x-www-form-urlencoded"}
HEADERS = {"Content-Type": "application/json"}

# Expect Wiz client_id, client_secret adn root_management_group_id to be passed in as runtime variables.

client_id = sys.argv[1]
client_secret = sys.argv[2]

# Where to run the query from- i.e. the root management group id.
root_management_group_id = sys.argv[3]

# Uncomment the following section to define the proxies in your environment,
#   if necessary:
# http_proxy  = "http://"+user+":"+passw+"@x.x.x.x:abcd"
# https_proxy = "https://"+user+":"+passw+"@y.y.y.y:abcd"
# proxyDict = {
#     "http"  : http_proxy,
#     "https" : https_proxy
# }

# The GraphQL query that defines which data you wish to fetch.
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

def model_project_structure(results):

    structure = {}

    for result in results:
        entities = result["entities"]

        if entities[0] != None:

            #entity0: tenant root group

            element                 = {}
            element["child-fps"]    = {}
            element["projects"]     = set()

            if entities[0]["name"] not in structure.keys():
                structure[entities[0]["name"]] = element

            #entity1: cloud organization - member of entity0 tenant root group

            element                 = {}
            element["child-fps"]    = {}
            element["projects"]     = set()

            if entities[1]["name"] not in structure[entities[0]["name"]]["child-fps"].keys():
                structure[entities[0]["name"]]["child-fps"][entities[1]["name"]] = element

            #entity2: subscription - member of entity1 cloud org
            
            if entities[2] != None:
                if entities[2]["name"] not in structure[entities[0]["name"]]["projects"]:
                    structure[entities[0]["name"]]["child-fps"][entities[1]["name"]]["projects"].add(entities[2]["name"])

            #entity3: cloud organization - member of entity1 cloud org

            if entities[3] != None:
                if entities[3]["name"] not in structure[entities[0]["name"]]["child-fps"][entities[1]["name"]]["child-fps"]:
                    element                 = {}
                    element["child-fps"]    = {}
                    element["projects"]     = set()
                    structure[entities[0]["name"]]["child-fps"][entities[1]["name"]]["child-fps"][entities[3]["name"]] = element

            #entity4: subscription - member of entity3 cloud org

            if entities[4] != None:
                if entities[4]["name"] not in structure[entities[0]["name"]]["child-fps"][entities[1]["name"]]["child-fps"][entities[3]["name"]]["projects"]:
                    structure[entities[0]["name"]]["child-fps"][entities[1]["name"]]["child-fps"][entities[3]["name"]]["projects"].add(entities[4]["name"])

            #entity5: subscription - member of tenant root management group

            if entities[5] != None:
                if entities[5]["name"] not in structure[entities[0]["name"]]["projects"]:
                    structure[entities[0]["name"]]["projects"].add(entities[5]["name"])

    return structure

def build_project_structure(structure):

    print(structure)
    print()
    print()

    # Process level 1 folder projects
    for l1fp in structure:
        print("Creating folder project: " + l1fp)
        mock_create_project(l1fp + "/")
        print()

        # Process child projects of level 1 folder projects
        print(" Processing child projects of " + l1fp + "...")
        if structure[l1fp]["projects"] == None:
            print("- None found.")
        for project in structure[l1fp]["projects"]:
            print()
            print("  * Creating project: " + l1fp + "/" + project)
            mock_create_project(l1fp + "/" + project)

        # Process child folder projects of level 1 folder projects
        print()
        print(" Processing child folder projects of " + l1fp + "...")
        for l2fp in structure[l1fp]["child-fps"]:
            print()
            print("  * Creating folder project: " + l1fp + "/" + l2fp + "...")
            mock_create_project(l1fp + "/" + l2fp + "/")

            # Process child projects of level 2 folder projects
            print()
            print("    Processing child projects of " + l1fp + "/" + l2fp + "...")
            if len(structure[l1fp]["child-fps"][l2fp]["projects"]) == 0:
                print("     - None found.")
            for project in structure[l1fp]["child-fps"][l2fp]["projects"]:
                print("     * Creating project: " + project)
                mock_create_project(l1fp + "/" + l2fp + "/" + project)
            print()

            # Process child folder projects of level 2 folder projects
            print("    Processing child folder projects of " + l1fp + "/" + l2fp + "...")
            if len(structure[l1fp]["child-fps"][l2fp]["child-fps"]) == 0:
                print("     - None found.")
            for l3fp in structure[l1fp]["child-fps"][l2fp]["child-fps"]:
                print()
                print("     * Creating folder project " + l1fp + "/" + l2fp + "/" + l3fp)
                mock_create_project(l1fp + "/" + l2fp + "/" + l3fp + "/")
                
                # Process child projects of level 3 folder projects
                print()
                print("       Processing child projects of " + l1fp + "/" + l2fp + "/" + l3fp +  "...")
                for project in structure[l1fp]["child-fps"][l2fp]["child-fps"][l3fp]["projects"]:
                    print("        * Creating project: " + project)
                    mock_create_project(l1fp + "/" + l2fp + "/" + l3fp + "/" + project)
                print()

                 # Process child folder projects of level 3 folder projects
                for l4fp in structure[l1fp]["child-fps"][l2fp]["child-fps"][l3fp]["child-fps"]:
                    print("creating folder project " + l1fp + "/" + l2fp + "/" + l3fp + "/" + l4fp)
                    mock_create_project(l1fp + "/" + l2fp + "/" + l3fp + "/" + l4fp + "/")

def create_project(project_name, is_folder, parent_folder_project_id):
    # The GraphQL query that defines which data you wish to fetch.
    query = ("""
        mutation CreateProject($input: CreateProjectInput!) {
            createProject(input: $input) {
            project {
                id
            }
            }
        }
    """)

    # The variables sent along with the above query
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


def mock_create_project(project_path):
    f = open("output.txt","a")
    f.write(project_path + "\n")

def main():

#    print("Getting token.")
    request_wiz_api_token(client_id, client_secret)

    result = query_wiz_api(query, variables)
    json_object = json.dumps(result)
    
    project_structure = model_project_structure(result["data"]["graphSearch"]["nodes"])

    build_project_structure(project_structure)

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