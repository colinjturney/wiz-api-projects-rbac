# Wiz API Projects and RBAC Setup Automation

# Disclaimer - PLEASE READ

By using this software and associated documentation files (the “Software”) you hereby agree and understand that:

1. The use of the Software is free of charge and may only be used by Wiz customers for its internal purposes.
2. The Software should not be distributed to third parties.
3. The Software is not part of Wiz’s Services and is not subject to your company’s services agreement with Wiz.
4. THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL WIZ BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE USE OF THIS SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Description

The aim of this script is to automate the creation of a project structure within Wiz based upon a Management Group/Organizational Unit structure held within Wiz's security graph- i.e. from a Cloud environment that is already connected to Wiz.

It also aims to build an RBAC structure based upon the user accounts that have role bindings mapped to each subscription.

## Limitations to current functionality

The script currently operates in a read-only mode and currently only focuses on the Azure Cloud Platform. The code has NOT yet been written to perform mutations on the Wiz API to actually create projects or provision users. Instead it will  generate three CSV files as follows:
* mock_project_output.csv: Details the projects it would create within Wiz.
* mock_user_output.csv: Detailing the users/roles that would be provisioned.

The idea behind generating these CSV files is so that it can be verified that the intended project structures and RBAC mappings are correct before being implemented for real.

An additional CSV file is also generated, user_import_file.csv. This is a file in a format that can then be imported into Wiz using a 
pre-existing API recipe which is at https://docs.wiz.io/wiz-docs/docs/api-recipes#bulk-create-pre-provision-saml-users-from-csv

## Output Files

* mock_project_output.csv: Details the projects that would be created within Wiz, with the following fields:
    * Project Name (string): The name of the project being created.
    * Project Path (string): The path to this project, through folder projects that contain it.
    * Is Folder (bool): Details whether this would be created as a folder project.
    * Project ID (string): A mocked identifier to this project. Intended as a placeholder to the identifier generated by Wiz when the project is created through the call to the Wiz API
    * Parent Project ID (string): Reference to the parent folder project ID that this project would be created within.
    * Nesting Depth: The depth in the folder project tree that this project resides within.
    * Originating Cloud: The cloud that this project relates to.

* mock_ad_groups.csv:
    * Group Name: The name of the AD group that is recommended to be created. This name must be defined by the script so it can be applied to the appropriate projects in saml_role_mappings.csv
    * Wiz Project: The name of the Wiz project that matches this AD group.
    * Member Name: The name of the user/member of the AD group. Currently this does not exclude any users (e.g. admin or service accounts) but customisation could be built if needed.
    * Member UPN/Email: The userPrincipalName or name attribute of the user.
    * Originating Cloud: The cloud that this AD group relates to.

* saml_role_mappings.csv:
    * Group Name: The name of the corresponding AD group to this role mapping.
    * Role: The name of the Wiz Role that would be scoped to this saml role mapping.
    * Project Name: The name of the project(s) that are scoped to this role.
    * Scoped User Count: The number of users scoped to this particular project- i.e. the number of usersthat the script identified that should be in the AD group that should be created for access to this role.
    * Originating Cloud: The cloud that this SAML role mapping relates to.

Group Name,Role,Project Name, Scoped User Count,Originating Cloud

    * Group Name: The name of the AD group that is recommended to be created. This name must be defined by the script so it can be applied to the appropriate projects in saml_role_mappings.csv
    * Wiz Project: The name of the Wiz project that matches this AD group.
    * Member Name: The name of the user/member of the AD group. Currently this does not exclude any users (e.g. admin or service accounts) but customisation could be built if needed.
    * Member UPN/Email: The userPrincipalName or name attribute of the user.
    * Originating Cloud: The cloud that this AD group relates to.

# How to run the script

It's recommended to ensure you have a Python virtualenv set up, using the `requirements.txt` file provided in this repository.

Make sure to create a Wiz Service Account with ONLY the following permission across all projects:
* Type: `Custom Integration (GraphQL API)`
* Project Scope: `All Projects`
* API Scope: `read:all`

Once loaded, create a script called `run.sh` or similar, structured similar to below:

```
export CLIENT_ID="[WIZ_CLIENT_ID]"
export CLIENT_SECRET="[WIZ_CLIENT_SECRET]"
export AZURE_ROOT_WIZ_PROJECT_NAME = "[AZURE_ROOT_WIZ_PROJECT_NAME]"
export AZURE_ROOT_MG_LIST="[AZURE_ROOT_MG_LIST]"
export DEFAULT_SAML_PROVIDER="[SAML_PROVIDER]"
export DEFAULT_USER_ROLE="[WIZ_USER_ROLE]"
export LOGGING_LEVEL="[LOGGING_LEVEL]"
export WIZ_DATACENTER="[WIZ_DATACENTER]"
export GCP_ROOT_WIZ_PROJECT_NAME="[GCP_ROOT_WIZ_PROJECT_NAME]"
export GCP_ROOT_ORG_LIST="[GCP_ROOT_ORG_LIST]"
export AWS_ROOT_WIZ_PROJECT_NAME="[AWS_ROOT_WIZ_PROJECT_NAME]"
export AWS_ROOT_ORG_LIST="[AWS_ROOT_ORG_LIST]"
export WRITE_MODE="[WRITE_MODE]"

python create_folder_projects.py "${CLIENT_ID}" "${CLIENT_SECRET}" "${AZURE_ROOT_WIZ_PROJECT_NAME}" "${AZURE_ROOT_MG_LIST}" "${DEFAULT_SAML_PROVIDER}" "${DEFAULT_USER_ROLE}" "${LOGGING_LEVEL}" "${WIZ_DATACENTER}" "${GCP_ROOT_WIZ_PROJECT_NAME}" "${GCP_ROOT_ORG_LIST}" "${AWS_ROOT_WIZ_PROJECT_NAME}" "${AWS_ROOT_ORG_LIST}" "${WRITE_MODE}"

```

Where the [values] above align to as follows:

* WIZ_CLIENT_ID: The client id from the generated Wiz service account
* WIZ_CLIENT_SECRET: The client secret from the generated Wiz service account
* AZURE_ROOT_WIZ_PROJECT_NAME: The name of the root Wiz project that will be used to group together all Azure-related folder projects and projects.
* AZURE_ROOT_MG_LIST: A JSON representation of all root management groups that should be included from Azure. For each root management group this should include a "friendly name", the provider ID of the management group and a list of "burner" management groups if applicable. Example value: `"[{\"friendly_name\": \"Azure MgtGroup A\", \"group_id\": \"tenantId/abc1234567890/providers/Microsoft.Management/managementGroups/abc1234567890\", \"burner_list\": [\"tenantId/abc1234567890/providers/Microsoft.Management/managementGroups/Burnerprojects\"]},{\"friendly_name\": \"Azure MgtGroup B\", \"group_id\": \"tenantId/abc1234567890/providers/Microsoft.Management/managementGroups/abc1234567890\",\"burner_list\":[]}]"`
* SAML_PROVIDER: The name of the SAML provider being used.
* WIZ_USER_ROLE: The project-scoped Wiz RBAC role to assign to all groupings generated by default - it is suggested to use `ProjectReader`.
* LOGGING_LEVEL: A lower case string set to "debug", "info" "warning" "error" "critical". Leave unset to not set a logging level.
* WIZ_DATACENTER: A lower case string set to the name of the Wiz DC used by your tenant (e.g. eu7)
* GCP_ROOT_WIZ_PROJECT_NAME: The name of the root Wiz project that will be used to group together all GCP-related folder projects and projects.
* GCP_ROOT_ORG_LIST: A JSON representation of all root organizations that should be included from GCP. For each root organization this should include a "friendly name", the provider ID of the management group and a list of "burner" management groups if applicable. Example value: `"[{\"friendly_name\": \"GCP Org A\", \"group_id\": \"01234567890\", \"burner_list\": [\"01234567890\"]},{\"friendly_name\": \"GCP Org B\", \"group_id\": \"01234567890\", \"burner_list\": []}]"`
* AWS_ROOT_WIZ_PROJECT_NAME: The name of the root Wiz project that will be used to group together all GCP-related folder projects and projects.
* AWS_ROOT_ORG_LIST: A JSON representation of all root organizations that should be included from AWS. For each root organization this should include a "friendly name", the provider ID of the management group and a list of "burner" management groups if applicable. Example value: `"[{\"friendly_name\": \"AWS Org A\", \"group_id\": \"r-abcd\", \"burner_list\":[]},{\"friendly_name\": \"AWS Org B\", \"group_id\": \"r-abcd\", \"burner_list\":[]},{\"friendly_name\": \"AWS Org C\", \"group_id\": \"r-abcd\", \"burner_list\":[]}]"`
* WRITE_MODE: `True` or `False`, depending on whether you want the script to attempt to actually create projects on Wiz.