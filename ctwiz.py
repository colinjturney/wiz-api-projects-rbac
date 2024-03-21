import requests
import logging

# Standard headers
HEADERS_AUTH = {"Content-Type": "application/x-www-form-urlencoded"}
HEADERS = {"Content-Type": "application/json"}

def query_wiz_api(query, variables, wiz_dc):
    """Query Wiz API for the given query data schema"""
    data = {"variables": variables, "query": query}

    try:
        # Uncomment the next first line and comment the line after that
        # to run behind proxies
        # result = requests.post(url="https://api.us20.app.wiz.io/graphql",
        #                        json=data, headers=HEADERS, proxies=proxyDict)
        result = requests.post(url="https://api." + wiz_dc + ".app.wiz.io/graphql",
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

def get_qry_vars_grp_members_for_subscriptions(external_id, cloud):

  if cloud != "AWS":

    return {
      "quick": False,
      "fetchPublicExposurePaths": True,
      "fetchInternalExposurePaths": False,
      "fetchIssueAnalytics": False,
      "fetchLateralMovement": True,
      "fetchKubernetes": False,
      "first": 500,
      "query": {
          "type": [
            "USER_ACCOUNT"
          ],
          "select": True,
          "where": {
            "userDirectory": {
              "EQUALS": [
                cloud
              ]
            }
          },
          "relationships": [
            {
              "type": [
                {
                  "type": "ASSIGNED_TO",
                  "reverse": True
                }
              ],
              "with": {
                "type": [
                  "ACCESS_ROLE_BINDING"
                ],
                "relationships": [
                  {
                    "type": [
                      {
                        "type": "APPLIES_TO"
                      }
                    ],
                    "with": {
                      "type": [
                        "SUBSCRIPTION"
                      ],
                      "where": {
                        "cloudPlatform": {
                          "EQUALS": [
                            cloud
                          ]
                        },
                        "externalId": {
                          "EQUALS": [
                            external_id
                          ]
                        }
                      }
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
  else:
     return {
      "quick": False,
      "fetchPublicExposurePaths": True,
      "fetchInternalExposurePaths": False,
      "fetchIssueAnalytics": False,
      "fetchLateralMovement": True,
      "fetchKubernetes": False,
      "first": 500,
      "query": {
          "type": [
            "USER_ACCOUNT"
          ],
          "select": True,
          "where": {
            "userDirectory": {
              "EQUALS": [
                cloud
              ]
            }
          },
          "relationships": [
            {
              "type": [
                {
                  "type": "ENTITLES",
                  "reverse": True
                }
              ],
              "with": {
                "type": [
                  "IAM_BINDING"
                ],
                "relationships": [
                  {
                    "type": [
                      {
                        "type": "ALLOWS_ACCESS_TO"
                      }
                    ],
                    "with": {
                      "type": [
                        "SUBSCRIPTION"
                      ],
                      "where": {
                        "cloudPlatform": {
                          "EQUALS": [
                            cloud
                          ]
                        },
                        "externalId": {
                          "EQUALS": [
                            external_id
                          ]
                        }
                      }
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

def get_qry_vars_grp_members_for_mgmt_groups(external_id, cloud):
  return {
    "quick": False,
    "fetchPublicExposurePaths": True,
    "fetchInternalExposurePaths": False,
    "fetchIssueAnalytics": False,
    "fetchLateralMovement": True,
    "fetchKubernetes": False,
    "first": 500,
    "query": {
      "type": [
        "USER_ACCOUNT"
      ],
      "select": True,
      "where": {
        "userDirectory": {
          "EQUALS": [
            cloud
          ]
        }
      },
      "relationships": [
        {
          "type": [
            {
              "type": "ASSIGNED_TO",
              "reverse": True
            }
          ],
          "with": {
            "type": [
              "ACCESS_ROLE_BINDING"
            ],
            "relationships": [
              {
                "type": [
                  {
                    "type": "APPLIES_TO"
                  }
                ],
                "with": {
                  "type": [
                    "CLOUD_ORGANIZATION"
                  ],
                  "where": {
                    "cloudPlatform": {
                      "EQUALS": [
                        cloud
                      ]
                    },
                    "externalId": {
                      "EQUALS": [
                        external_id
                      ]
                    }
                  }
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

def get_qry_grp_role_bindings():
    return ("""
    query GraphSearch($query: GraphEntityQueryInput, $controlId: ID, $projectId: String!, $first: Int, $after: String, $fetchTotalCount: Boolean!, $quick: Boolean = true, $fetchPublicExposurePaths: Boolean = false, $fetchInternalExposurePaths: Boolean = false, $fetchIssueAnalytics: Boolean = false, $fetchLateralMovement: Boolean = false, $fetchKubernetes: Boolean = false) {
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
            otherSubscriptionExposures(first: 10) @include(if: $fetchInternalExposurePaths) {
              nodes {
                ...NetworkExposureFragment
              }
            }
            otherVnetExposures(first: 10) @include(if: $fetchInternalExposurePaths) {
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
      issueAnalytics: issues(filterBy: {status: [IN_PROGRESS, OPEN]}) @include(if: $fetchIssueAnalytics) {
        highSeverityCount
        criticalSeverityCount
      }
      typedProperties {
        ... on GEEndpoint {
          dynamicScannerScreenshotUrl
        }
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

def get_qry_vars_grp_azure_role_bindings_for_subscriptions(subscription_id):
    return {
  "quick": False,
  "fetchPublicExposurePaths": True,
  "fetchInternalExposurePaths": False,
  "fetchIssueAnalytics": False,
  "fetchLateralMovement": True,
  "fetchKubernetes": False,
  "first": 50,
  "query": {
    "type": [
      "GROUP"
    ],
    "where": {
      "nativeType": {
        "EQUALS": [
          "Group"
        ]
      }
    },
    "select": True,
    "relationships": [
      {
        "type": [
          {
            "type": "ENTITLES",
            "reverse": True
          }
        ],
        "with": {
          "type": [
            "IAM_BINDING"
          ],
          "relationships": [
            {
              "type": [
                {
                  "type": "ALLOWS_ACCESS_TO"
                }
              ],
              "with": {
                "type": [
                  "SUBSCRIPTION",
                ],
                "where": {
                  "nativeType": {
                    "EQUALS": [
                      "Microsoft.Subscription",
                    ]
                  },
                  "externalId": {
                    "EQUALS": [
                      subscription_id
                    ]
                  }
                }
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

def get_qry_vars_grp_azure_role_bindings_for_mgmtgrp(management_group_id):
     return {
      "quick": False,
      "fetchPublicExposurePaths": True,
      "fetchInternalExposurePaths": False,
      "fetchIssueAnalytics": False,
      "fetchLateralMovement": True,
      "fetchKubernetes": False,
      "first": 50,
      "query": {
        "type": [
          "GROUP"
        ],
        "where": {
          "nativeType": {
            "EQUALS": [
              "Group"
            ]
          }
        },
        "select": True,
        "relationships": [
          {
            "type": [
              {
                "type": "ENTITLES",
                "reverse": True
              }
            ],
            "with": {
              "type": [
                "IAM_BINDING"
              ],
              "relationships": [
                {
                  "type": [
                    {
                      "type": "ALLOWS_ACCESS_TO"
                    }
                  ],
                  "with": {
                    "type": [
                      "CLOUD_ORGANIZATION",
                    ],
                    "where": {
                      "nativeType": {
                        "EQUALS": [
                          "Microsoft.Management/managementGroups",
                        ]
                      },
                      "externalId": {
                        "EQUALS": [
                          management_group_id
                        ]
                      }
                    }
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

def get_qry_vars_grp_aws_role_bindings_for_subscriptions(subscription_id):
  return {
  "quick": False,
  "fetchPublicExposurePaths": True,
  "fetchInternalExposurePaths": False,
  "fetchIssueAnalytics": False,
  "fetchLateralMovement": True,
  "fetchKubernetes": False,
  "first": 500,
  "query": {
    "type": [
      "GROUP"
    ],
    "select": True,
    "relationships": [
      {
        "type": [
          {
            "type": "ENTITLES",
            "reverse": True
          }
        ],
        "with": {
          "type": [
            "IAM_BINDING"
          ],
          "where": {
            "accessTypes": {
              "EQUALS": [
                "Impersonate"
              ]
            },
            "name": {
              "EQUALS": [
                "AWS sts:AssumeRoleWithSAML permission"
              ]
            }
          },
          "relationships": [
            {
              "type": [
                {
                  "type": "ALLOWS_ACCESS_TO"
                }
              ],
              "with": {
                "type": [
                  "PRINCIPAL"
                ],
                "relationships": [
                  {
                    "type": [
                      {
                        "type": "CONTAINS",
                        "reverse": True
                      }
                    ],
                    "with": {
                      "type": [
                        "SUBSCRIPTION"
                      ],
                      "where": {
                        "externalId": {
                          "EQUALS": [
                            subscription_id
                          ]
                        }
                      }
                    }
                  }
                ]
              }
            }
          ]
        }
      }
    ],
    "where": {
      "nativeType": {
        "EQUALS": [
          "ssoGroup"
        ]
      }
    }
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

def get_qry_vars_azure_project_structure_excl_burners(root_management_group_id, burner_mg_id):
  return {
  "quick": False,
  "fetchPublicExposurePaths": True,
  "fetchInternalExposurePaths": False,
  "fetchIssueAnalytics": False,
  "fetchLateralMovement": True,
  "fetchKubernetes": False,
  "first": 500,
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
      },
      "cloudPlatform": {
        "EQUALS": [
          "Azure"
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
                                        ],
                                        "where": {
                                          "externalId": {
                                            "NOT_EQUALS": [
                                              burner_mg_id
                                            ]
                                          }
                                        }
                                      }
                                    },
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
                                  ],
                                  "where": {
                                    "externalId": {
                                      "NOT_EQUALS": [
                                        burner_mg_id
                                      ]
                                    }
                                  }
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
                            ],
                            "where": {
                              "externalId": {
                                "NOT_EQUALS": [
                                  burner_mg_id
                                ]
                              }
                            }
                          }
                        }
                      ],
                      "where": {
                        "externalId": {
                          "NOT_EQUALS": [
                            burner_mg_id
                          ]
                        }
                      }
                    }
                  }
                ],
                "where": {
                  "externalId": {
                    "NOT_EQUALS": [
                      burner_mg_id
                    ]
                  }
                }
              }
            }
          ],
          "where": {
            "externalId": {
              "NOT_EQUALS": [
                burner_mg_id
              ]
            }
          }
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

def get_qry_vars_azure_project_structure_burners(root_management_group_id, burner_mg_id):
  return {
    "quick": False,
    "fetchPublicExposurePaths": True,
    "fetchInternalExposurePaths": False,
    "fetchIssueAnalytics": False,
    "fetchLateralMovement": True,
    "fetchKubernetes": False,
    "first": 500,
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
        },
        "cloudPlatform": {
          "EQUALS": [
            "Azure"
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
                                      },
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
                            }
                          }
                        ]
                      }
                    }
                  ],
                  "where": {
                    "externalId": {
                      "EQUALS": [
                        burner_mg_id
                      ]
                    }
                  }
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

def get_qry_vars_project_structure_no_burners(root_management_group_id, cloud):
  return {
  "quick": False,
  "fetchPublicExposurePaths": True,
  "fetchInternalExposurePaths": False,
  "fetchIssueAnalytics": False,
  "fetchLateralMovement": True,
  "fetchKubernetes": False,
  "first": 500,
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
      },
      "cloudPlatform": {
        "EQUALS": [
          cloud
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
                                    },
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
                          }
                        }
                      ]
                    }
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

def get_qry_vars_gcp_project_structure_excl_burners(root_management_group_id, burner_mg_id):
  return {
    "quick": False,
    "fetchPublicExposurePaths": True,
    "fetchInternalExposurePaths": False,
    "fetchIssueAnalytics": False,
    "fetchLateralMovement": True,
    "fetchKubernetes": False,
    "first": 500,
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
        },
        "cloudPlatform": {
          "EQUALS": [
            "GCP"
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
          "optional": True,
          "with": {
            "type": [
              "CLOUD_ORGANIZATION"
            ],
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
                                }
                              ],
                              "select": True
                            }
                          }
                        ],
                        "select": True
                      }
                    }
                  ],
                  "select": True,
                  "where": {
                    "externalId": {
                      "NOT_EQUALS": [
                        burner_mg_id
                      ]
                    }
                  }
                }
              }
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

def get_qry_vars_aws_project_structure(root_management_group_id):
  return {
    "quick": False,
    "fetchPublicExposurePaths": True,
    "fetchInternalExposurePaths": False,
    "fetchIssueAnalytics": False,
    "fetchLateralMovement": True,
    "fetchKubernetes": False,
    "first": 500,
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
                ],
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

def get_qry_vars_create_folder_project(project_name, parent_folder_project_id):
    return {
        "input": {
            "name": project_name,
            "identifiers": [],
            "isFolder": True,
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
        }, 
      "projectId": "*",
      "fetchTotalCount": False
    }

def get_qry_vars_create_project_subscription(project_name, subscription_id, parent_folder_project_id):
    return {
        "input": {
            "name": project_name,
            "identifiers": [],
            "isFolder": False,
            "cloudAccountLinks": [
              {
                "cloudAccount": subscription_id,
                "environment": "PRODUCTION",
                "shared": False
              }
            ],
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

def get_qry_all_projects():

  return """
    query ProjectsTable($filterBy: ProjectFilters, $first: Int, $after: String, $orderBy: ProjectOrder, $analyticsSelection: ProjectIssueAnalyticsSelection, $fetchOverdueAndCreatedVsResolvedTrend: Boolean!, $trendStartDate: DateTime!, $trendEndDate: DateTime!, $trendInterval: TimeInterval!) {
      projects(filterBy: $filterBy, first: $first, after: $after, orderBy: $orderBy) {
        nodes {
          id
          name
          slug
          isFolder
          childProjectCount
          cloudAccountCount
          repositoryCount
          kubernetesClusterCount
          containerRegistryCount
          securityScore
          archived
          businessUnit
          description
          workloadCount
          licensedWorkloadQuota
          riskProfile {
            businessImpact
          }
          issueAnalytics(selection: $analyticsSelection) {
            issueCount
            informationalSeverityCount
            lowSeverityCount
            mediumSeverityCount
            highSeverityCount
            criticalSeverityCount
          }
          nestingLevel
          ancestorProjects {
            ...ProjectsBreadcrumbsItemDetails
          }
          openIssuesTrend: issuesTrend(
            type: OPEN_ISSUES
            startDate: $trendStartDate
            endDate: $trendEndDate
            interval: $trendInterval
          ) {
            type
            dataPoints {
              time
              highSeverityValue
              criticalSeverityValue
            }
          }
          overdueIssuesTrend: issuesTrend(
            type: OVERDUE_ISSUES
            startDate: $trendStartDate
            endDate: $trendEndDate
            interval: $trendInterval
          ) @include(if: $fetchOverdueAndCreatedVsResolvedTrend) {
            type
            dataPoints {
              time
              highSeverityValue
              criticalSeverityValue
            }
          }
        
        }
        pageInfo {
          hasNextPage
          endCursor
        }
        totalCount
      }
    }
    
        fragment ProjectsBreadcrumbsItemDetails on Project {
      id
      name
      isFolder
    }
"""

# The variables sent along with the above query
def get_qry_vars_parent_project(project_id, is_root, include_archived):
  return {
    "first": 50,
    "filterBy": {
      "id": {
        "equals": [
          project_id
        ]
      },
      "root": is_root,
      "includeArchived": include_archived
    },
    "orderBy": {
      "field": "IS_FOLDER",
      "direction": "DESC"
    },
    "analyticsSelection": {},
    "trendStartDate": "2024-02-21T00:00:00.000Z",
    "trendEndDate": "2024-03-21T23:59:59.999Z",
    "trendInterval": "DAY",
    "fetchOverdueAndCreatedVsResolvedTrend": True
  }
   
def get_qry_vars_child_projects(parent_project_id, include_archived):
  return {
    "first": 50,
    "filterBy": {
      "parentProjectId": parent_project_id,
      "includeArchived": include_archived
    },
    "orderBy": {
      "field": "IS_FOLDER",
      "direction": "DESC"
    },
    "analyticsSelection": {},
    "trendStartDate": "2024-02-21T00:00:00.000Z",
    "trendEndDate": "2024-03-21T23:59:59.999Z",
    "trendInterval": "DAY",
    "fetchOverdueAndCreatedVsResolvedTrend": True
  }

# {
#   "data": {
#     "createProject": {
#       "project": {
#         "id": "7d7522ae-e5ea-5695-a631-1cc28a358abf"
#       }
#     }
#   }
# }