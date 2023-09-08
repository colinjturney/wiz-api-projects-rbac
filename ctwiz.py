import requests
import logging

# Standard headers
HEADERS_AUTH = {"Content-Type": "application/x-www-form-urlencoded"}
HEADERS = {"Content-Type": "application/json"}

def query_wiz_api(query, variables):
    """Query Wiz API for the given query data schema"""
    data = {"variables": variables, "query": query}

    try:
        # Uncomment the next first line and comment the line after that
        # to run behind proxies
        # result = requests.post(url="https://api.us20.app.wiz.io/graphql",
        #                        json=data, headers=HEADERS, proxies=proxyDict)
        result = requests.post(url="https://api.us20.app.wiz.io/graphql",
                               json=data, headers=HEADERS, timeout=60)

    except Exception as e:
        if ('502: Bad Gateway' not in str(e) and
                '503: Service Unavailable' not in str(e) and
                '504: Gateway Timeout' not in str(e)):
            logging.ERROR("Wiz-API-Error: %s", str(e))
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
                             headers=HEADERS_AUTH, data=auth_payload,  timeout=60)

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
        logging.ERROR(exception)
        raise Exception('Could not parse API response')
    HEADERS["Authorization"] = "Bearer " + TOKEN

    return TOKEN

def get_qry_role_bindings():

    return """
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
    """


def get_qry_vars_role_bindings(subscription_id):
    return {
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
                        subscription_id
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

def get_qry_project_structure():
    return """
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
    """

def get_qry_vars_project_structure(root_management_group_id):
    return {
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

def get_qry_create_project():
    return ("""
        mutation CreateProject($input: CreateProjectInput!) {
            createProject(input: $input) {
            project {
                id
            }
            }
        }
    """)

def get_qry_vars_create_project(project_name, is_folder, parent_folder_project_id):
    return {
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