# Python 3.6+
# pip install gql==3.0.0a5 aiohttp==3.7.3
import http.client
import json
import csv
import logging
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

"""
Allowed role names for the CSV input file:
enum BuiltInUserRoleId {
  GLOBAL_ADMIN
  GLOBAL_READER
  GLOBAL_RESPONDER
  GLOBAL_CONTRIBUTOR
  GLOBAL_GRAPH_READER
  CONNECTOR_ADMIN
  CONNECTOR_READER
  PROJECT_ADMIN
  PROJECT_MEMBER
  PROJECT_READER
  PROJECT_GRAPH_READER
  DOCUMENTATION_READER
  SETTINGS_ADMIN
}
"""
client_id = ""
client_secret = ""
# client_id = os.getenv('wizcli_id')
# client_secret = os.getenv('wizcli_secret')

api_endpoint = "https://api.us20.app.wiz.io/graphql"
auth_endpoint = "auth.app.wiz.io"

logging.getLogger("gql").setLevel(logging.ERROR)

allowed_roles = [
  'GLOBAL_ADMIN',
  'GLOBAL_READER',
  'GLOBAL_RESPONDER',
  'GLOBAL_CONTRIBUTOR',
  'GLOBAL_GRAPH_READER',
  'CONNECTOR_ADMIN',
  'CONNECTOR_READER',
  'PROJECT_ADMIN',
  'PROJECT_MEMBER',
  'PROJECT_READER',
  'PROJECT_GRAPH_READER'
]

saml_idps_list_query = gql("""
  query SAMLIdentityProvidersTable(
      $first: Int
      $after: String
      $filterBy: SAMLIdentityProviderFilters
    ) {
      samlIdentityProviders(first: $first,
       after: $after, filterBy: $filterBy) {
        nodes {
          id
          name
          loginURL
        }
        pageInfo {
          hasNextPage
          endCursor
        }
        totalCount
      }
    }
""")

saml_idps_list_variables = {
  'first': 500,
  'filterBy': {
    'source': 'MODERN'
  }
}

saml_idp_query = gql("""
  query LoadSAMLIdentityProvider($id: ID!) {
      samlIdentityProvider(id: $id) {
        id
        name
        loginURL
        logoutURL
        useProviderManagedRoles
        certificate
        domains
        issuerURL
        mergeGroupsMappingByRole
        allowManualRoleOverride
        groupMapping {
          providerGroupId
          role {
            id
            name
            isProjectScoped
          }
          projects {
            id
            name
          }
        }
      }
    }
""")

saml_idp_variables = {
  'id': ''
}

patch_saml_query = gql("""
  mutation UpdateSAMLIdentityProvider(
      $input: UpdateSAMLIdentityProviderInput!
    ) {
      updateSAMLIdentityProvider(input: $input) {
        samlIdentityProvider {
          id
          name
        }
      }
    }
""")

patch_saml_variables = {
  'input': {
    'id': '',
    'patch': {
      'groupMapping': []
    }
  }
}


def checkAPIerrors(query, variables, access_token):
    transport = AIOHTTPTransport(
        url=api_endpoint,
        headers={'Authorization': 'Bearer ' + access_token}
    )
    client = Client(transport=transport,
                    fetch_schema_from_transport=False,
                    execute_timeout=55)

    try:
        result = client.execute(query, variable_values=variables)
    except Exception as e:
        if ('502: Bad Gateway' not in str(e)
           and '503: Service Unavailable' not in str(e)):
            logging.error("<p>Wiz-API-Error: %s</p>" % str(e))
            return(e)
        else:
            logging.info("Retry")

    return result


def getProjects(access_token, p_name):
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
        "first": 500,
        "filterBy": {
            "search": p_name
        },
        "orderBy": {
            "field": "SECURITY_SCORE",
            "direction": "ASC"
        }
    }

    result = checkAPIerrors(getProjectsquery,
                            getProjectsvariables,
                            access_token)

    return result['projects']['nodes']


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
            logging.error('Invalid Input.')
            return ask_user(input())
    except Exception as error:
        logging.error("Please enter valid inputs")
        logging.error(error)
        return ask_user(input())


def let_user_pick(options):
    print("Please choose a Wiz SAML connection to update:")
    for idx, element in enumerate(options):
        print("{}) {}".format(idx+1, element['name']))
    i = input("Enter number: ")
    try:
        if 0 < int(i) <= len(options):
            return options[int(i)-1]['id']
        else:
            logging.error('Invalid Input.')
            return let_user_pick(options)
    except Exception as error:
        logging.error("Please enter a valid input")
        logging.error(error)
        return let_user_pick(options)


def main():
    try:
        logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(message)s',  # noqa: 501
                            level=logging.INFO)

        logging.info("Reading the input file, so we can walk through it and create Projects.")  # noqa: E501
        with open('group-mappings-to-create.csv', newline='') as f:
            # Reading and ignoring the first line as it has the CSV headers...
            f.readline()
            reader = csv.reader(f, delimiter=',')
            mapping_input_from_file = list(reader)
        logging.info("Verifying CSV input file.")
        for mapping in mapping_input_from_file:
            if mapping[1] not in allowed_roles:
                logging.error(f"{mapping[1]} is not in the allowed list of",
                              "roles. Please fix the input file.",
                              f"Allowed roles are:\n{allowed_roles}")
                quit()
            if ('PROJECT' not in mapping[1] and mapping[2] != ''
               and mapping[2] is not None):
                logging.error(f"{mapping[1]} is a global role with a list of",
                              "projects assigned to it",
                              f"({mapping[2]}). Please fix the input file.")
                quit()

        logging.info("Create token...")
        token = request_wiz_api_token(client_id, client_secret)

        logging.info("Getting list of SAML provider settings in Wiz.")
        saml_providers = checkAPIerrors(saml_idps_list_query,
                                        saml_idps_list_variables, token)
        saml_choice = let_user_pick(saml_providers['samlIdentityProviders']['nodes'])  # noqa: E501
        SAML_conn_id = saml_choice

        logging.info("Reading existing SAML group mappings from SSO settings in Wiz...")  # noqa: E501
        saml_idp_variables['id'] = SAML_conn_id
        saml_config = checkAPIerrors(saml_idp_query, saml_idp_variables, token)
        existing_group_mappings = saml_config['samlIdentityProvider']['groupMapping']  # noqa: E501
        loginURL = saml_config['samlIdentityProvider']['loginURL']  # noqa: E501
        logoutURL = saml_config['samlIdentityProvider']['logoutURL']  # noqa: E501
        certificate = saml_config['samlIdentityProvider']['certificate']  # noqa: E501
        issuerURL = saml_config['samlIdentityProvider']['issuerURL']  # noqa: E501
        useProviderManagedRoles = saml_config['samlIdentityProvider']['useProviderManagedRoles']  # noqa: E501
        mergeGroupsMappingByRole = saml_config['samlIdentityProvider']['mergeGroupsMappingByRole']  # noqa: E501
        allowManualRoleOverride = saml_config['samlIdentityProvider']['allowManualRoleOverride']  # noqa: E501
        for egm in existing_group_mappings:
            """
            change role data from dict to str to prepare for patching.
            query output for role in groupMapping:
            "role": {
                "id": "PROJECT_READER",
                "name": "ProjectReader",
                "isProjectScoped": true
            }
            mutation input for patch:
            "role": "PROJECT_READER"
            AND:
            query output for project in groupMapping:
            "projects": [
                            {
                "id": "12345678-1234-54e1-a436-c20a02eac19c",
                "name": "blah"
                }
                        ]
            mutation input for patch:
            "projects": [
                            "12345678-1234-54e1-a436-c20a02eac19c"
                        ]
            """
            egm['role'] = egm['role']['id']
            if egm['projects'] is not None:
                new_projects_in_egm = []
                for project in egm['projects']:
                    new_projects_in_egm.append(project['id'])
                egm['projects'] = new_projects_in_egm
            """
            End patching transformation
            """

        logging.info("Starting to map SAML Group with from input file.")
        logging.info("Can we continue updating SAML group mapping entries if they already exist?")  # noqa: E501
        confirm_update_method = ask_user(input())
        
        if not confirm_update_method:
            logging.info("Per user input, not updating existing mappings, but rather only creating new mappings and skipping existing ones.")  # noqa: E501
            update_existing_mappings = False
        else:
            logging.info("Per user input, we\'ll also update existing mappings.")  # noqa: E501
            update_existing_mappings = True

        # Opening entries from the mapping CSV
        for mapping in mapping_input_from_file:

            mapping_project_scoped = False
            print("########################")
            if mapping[2] != '' and mapping[2] is not None:
                # if no projects - then global mapping, no fluff needed.
                logging.info(f"Mapping {mapping[0]} is project scoped.")
                mapping_project_scoped = True
                mapping_projects = mapping[2].split(",")
            else:
                logging.info(f"Mapping {mapping[0]} is global scoped.")
                mapping_project_scoped = False

            mapping_found = False

            # build list of existing mappings, so we can patch it
            for egm in existing_group_mappings:
                mapping_found = False
                if egm['providerGroupId'] == mapping[0]:
                    mapping_found = True
                    # current_mapping_projects = egm['projects']
                    break
                else:
                    mapping_found = False

            if not mapping_found:
                logging.info(f"Mapping {mapping[0]} not found in Wiz SSO settings. Adding to list for patching.")  # noqa: E501
                # create mapping. add to it.

                if mapping_project_scoped:
                    # project scope mapping, so building
                    # project list with details
                    new_project_list_to_add = []
                    for project in mapping_projects:
                        project_details = getProjects(token, project)
                        if (project_details != [] and project_details is not None):
                            
                            if len(project_details) > 1:
                                project_id = None
                                # corner case for name contains in projects
                                for pd in project_details:
                                    if pd['name'] == project:
                                        project_id = pd['id']
                                        new_project_list_to_add.append(project_id)
                                        break
                            elif len(project_details) == 0:
                                project_id = project_details[0]['id']
                                # project_name = project_details[0]['name']
                                    
                                new_project_list_to_add.append(project_id)
                            else:
                                logging.error(f"Project {project} does not exist in Wiz. Please create it first. Skipping this mapping.") # noqa: E501
                                
                    existing_group_mappings.append({"providerGroupId": mapping[0],"role": mapping[1],"projects": new_project_list_to_add})  # noqa: E501
                            
                else:
                    existing_group_mappings.append({"providerGroupId": mapping[0],"role": mapping[1]})
            else:
                logging.info(f"Mapping {mapping[0]} was found in Wiz SSO settings.") # noqa: E501
                if update_existing_mappings:
                    # build list here...
                    if mapping_project_scoped:
                        logging.info("Per user input, updating existing mapping. Getting Project details.")  # noqa: E501
                        # project scope mapping, so building
                        # project list with details
                        new_project_list_to_add = []
                        for project in mapping_projects:
                            project_details = getProjects(token, project)
                            if (project_details != [] and project_details is not None):
                                if len(project_details) > 1:
                                    # corner case for name contains in projects
                                    for pd in project_details:
                                        if pd['name'] == project:
                                            project_id = pd['id']
                                            # project_name = pd['name']
                                            break
                                else:
                                    project_id = project_details[0]['id']
                                new_project_list_to_add.append(project_id)
                            else:
                                logging.error(f"Project {project} does not exist",
                                              "in Wiz. Please create it first.",
                                              "Skipping this mapping.")
                    else:
                        logging.info("Per user input, updating existing mapping.")
                    for egm in existing_group_mappings:
                        if egm['providerGroupId'] == mapping[0]:
                            egm["role"] = mapping[1]
                            if mapping_project_scoped:
                                if new_project_list_to_add == []:
                                    new_project_list_to_add = None
                                break
                else:
                    logging.info("Per user input, NOT updating existing mapping. Skipping.")  # noqa: E501

        patch_saml_variables['input']['patch']['loginURL'] = loginURL  # noqa: E501
        patch_saml_variables['input']['patch']['logoutURL'] = logoutURL  # noqa: E501
        patch_saml_variables['input']['patch']['certificate'] = certificate  # noqa: E501
        patch_saml_variables['input']['patch']['issuerURL'] = issuerURL  # noqa: E501
        patch_saml_variables['input']['patch']['useProviderManagedRoles'] = useProviderManagedRoles  # noqa: E501
        patch_saml_variables['input']['patch']['mergeGroupsMappingByRole'] = mergeGroupsMappingByRole  # noqa: E501
        patch_saml_variables['input']['patch']['useProviderManagedRoles'] = useProviderManagedRoles  # noqa: E501
        patch_saml_variables['input']['patch']['allowManualRoleOverride'] = allowManualRoleOverride  # noqa: E501
        patch_saml_variables['input']['patch']['groupMapping'] = existing_group_mappings  # noqa: E501
        patch_saml_variables['input']['id'] = SAML_conn_id
        patch_saml_mapping = checkAPIerrors(patch_saml_query,
                                            patch_saml_variables, token)
        logging.info(patch_saml_mapping)

    except Exception as e:
        logging.error('An exception has been raised: {}'.format(e))


if __name__ == '__main__':
    main()
