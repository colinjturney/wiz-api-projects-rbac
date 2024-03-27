# Wiz API Projects and RBAC Setup Automation

## Table of Contents

<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [Wiz API Projects and RBAC Setup Automation](#wiz-api-projects-and-rbac-setup-automation)
- [Disclaimer - PLEASE READ](#disclaimer-please-read)
- [Description](#description)
- [Steps to follow](#steps-to-follow)
- [Individual Script Documentation](#individual-script-documentation)
   * [Script 1: 1-extract_project_adgroups_structure.py](#script-1-1-extract_project_adgroups_structurepy)
      + [Script 1: How to run the script](#script-1-how-to-run-the-script)
      + [Script 1: Expected Output](#script-1-expected-output)
   * [Script 2: 2-create_projects.py](#script-2-2-create_projectspy)
      + [Script 2: How to run the script](#script-2-how-to-run-the-script)
      + [Script 2: Expected Output](#script-2-expected-output)
   * [Script 3: 3-extract_saml_mappings.py](#script-3-3-extract_saml_mappingspy)
      + [Script 3: How to run the script](#script-3-how-to-run-the-script)
      + [Script 3: Expected Output](#script-3-expected-output)

<!-- TOC end -->

<!-- TOC --><a name="wiz-api-projects-and-rbac-setup-automation"></a>


<!-- TOC --><a name="disclaimer-please-read"></a>
# Disclaimer - PLEASE READ

By using this software and associated documentation files (the “Software”) you hereby agree and understand that:

1. The use of the Software is free of charge and may only be used by Wiz customers for its internal purposes.
2. The Software should not be distributed to third parties.
3. The Software is not part of Wiz’s Services and is not subject to your company’s services agreement with Wiz.
4. THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL WIZ BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE USE OF THIS SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- TOC --><a name="description"></a>
# Description

The three scripts in this repository aim to assist with automating the creation of a project structure within Wiz, based upon a Managemetn Group/Organizational Unit structure held within Wiz's security graph- i.e. from a Cloud environment that is already connected to Wiz.

The scripts also aim to build an RBAC structure based upon the user accounts that have role bindings mapped to each subscription.


<!-- TOC --><a name="steps-to-follow"></a>
# Steps to follow

1. Prepare a wrapper script for Script 1.
1. Run the wrapper script for Script 1.
1. Examine the output files of Script 1 for duplicate project names and reconcile these. Take care to edit the correct entry in both the `wiz-project-name` and `parentProjectName` columns.
1. Prepare a wrapper script for Script 2, with the appropriate project output file from script 1 set as the input file.
1. Run the wrapper script for Script 2.
1. Prepare a wrapper script for Script 3.
1. Run the wrapper script for Script 3.
1. Use the output file from Script 3 as input into the SAML Role Mappings recipe on the Wiz API recipes documentation.

<!-- TOC --><a name="individual-script-documentation"></a>
# Individual Script Documentation

<!-- TOC --><a name="script-1-1-extract_project_adgroups_structurepy"></a>
## Script 1: 1-extract_project_adgroups_structure.py

The purpose of this script is to generate two output files:
1. A CSV representation of all projects that should be created, based upon management groups and organizational units within the AWS, Azure and GCP organizations connected to the Wiz tenant.
2. A CSV representation of all AD groups, SSO users and the projects such users/groups should be mapped to.

<!-- TOC --><a name="script-1-how-to-run-the-script"></a>
### Script 1: How to run the script

It's recommended to ensure you have a Python virtualenv set up, using the `requirements.txt` file provided in this repository.

Make sure to create a Wiz Service Account with ONLY the following permission across all projects:
* Type: `Custom Integration (GraphQL API)`
* Project Scope: `All Projects`
* API Scope: `read:all`

Once loaded, create a wrapper bash script called `1-run.sh` or similar, structured similar to below:

```
export WIZ_CLIENT_ID="[WIZ_CLIENT_ID]"
export WIZ_CLIENT_SECRET="[WIZ_CLIENT_SECRET]"
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
export PROJECT_OUTPUT_FILE="PROJECT_OUTPUT_FILE"
export AD_OUTPUT_FILE="AD_OUTPUT_FILE"

python 1-extract_project_adgroups_structure.py "${WIZ_CLIENT_ID}" "${WIZ_CLIENT_SECRET}" "${AZURE_ROOT_WIZ_PROJECT_NAME}" "${AZURE_ROOT_MG_LIST}" "${DEFAULT_SAML_PROVIDER}" "${DEFAULT_USER_ROLE}" "${LOGGING_LEVEL}" "${WIZ_DATACENTER}" "${GCP_ROOT_WIZ_PROJECT_NAME}" "${GCP_ROOT_ORG_LIST}" "${AWS_ROOT_WIZ_PROJECT_NAME}" "${AWS_ROOT_ORG_LIST}" "${PROJECT_OUTPUT_FILE}" "${AD_OUTPUT_FILE}"

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
* PROJECT_OUTPUT_FILE: The name of the file that you want to output the list of projects that would be created (CSV format)
* AD_OUTPUT_FILE: The name of the file that you want to output the list of user, ad group and Wiz project mappings to.

<!-- TOC --><a name="script-1-expected-output"></a>
### Script 1: Expected Output

The script will output two files. 

**IMPORTANT NOTE** - The script does not validate the project names that would be created in any way. You are strongly advised to examine the outputs of script 1 and correct any duplicate project/folder-project names accordingly. Note that it is not possible to easily cater for duplicate project names through the approach we are following here, therefore these should be corrected in the output files of Script 1, prior to proceeding to Script 2.

#### Script 1: Output File 1: PROJECT_OUTPUT_FILE.csv

The output of this script will be as follows. This is the list of projects and folder projects that should be created by script 2. 

|wiz-project-name    |isFolder|cloudAccountLinks     |cloudOrganizationLinks|parentProjectName   |Full Path                                                                 |Path Depth|Cloud|
|--------------------|--------|----------------------|----------------------|--------------------|--------------------------------------------------------------------------|----------|-----|
|Colin-Turney-Azure-1|TRUE    |None                  |                      |                    |Colin-Turney-Azure-1                                                      |1         |Azure|
|Colin-Azure-MgtGroup|TRUE    |cloudaccountexternalid|                      |Colin-Turney-Azure-1|Colin-Turney-Azure-1/Colin-Azure-MgtGroup                                 |2         |Azure|
|Outpost             |TRUE    |cloudaccountexternalid|                      |Colin-Azure-MgtGroup|Colin-Turney-Azure-1/Colin-Azure-MgtGroup/Outpost                         |3         |Azure|
|Outpost             |FALSE   |cloudaccountexternalid|                      |Outpost             |Colin-Turney-Azure-1/Colin-Azure-MgtGroup/Outpost/Outpost                 |4         |Azure|
|Colin-Wiz           |FALSE   |cloudaccountexternalid|                      |Colin-Azure-MgtGroup|Colin-Turney-Azure-1/Colin-Azure-MgtGroup/Colin-Wiz                       |3         |Azure|
|CT-Mg1              |TRUE    |cloudaccountexternalid|                      |Colin-Azure-MgtGroup|Colin-Turney-Azure-1/Colin-Azure-MgtGroup/CT-Mg1                          |3         |Azure|
|CT-Mg1-Su1          |FALSE   |cloudaccountexternalid|                      |CT-Mg1              |Colin-Turney-Azure-1/Colin-Azure-MgtGroup/CT-Mg1/CT-Mg1-Su1               |4         |Azure|
|CT-Mg1-Mg1          |TRUE    |cloudaccountexternalid|                      |CT-Mg1              |Colin-Turney-Azure-1/Colin-Azure-MgtGroup/CT-Mg1/CT-Mg1-Mg1               |4         |Azure|
|CT-Mg1-Mg1-Su1      |FALSE   |cloudaccountexternalid|                      |CT-Mg1-Mg1          |Colin-Turney-Azure-1/Colin-Azure-MgtGroup/CT-Mg1/CT-Mg1-Mg1/CT-Mg1-Mg1-Su1|5         |Azure|
|CT-Mg1-Mg1-Mg1      |TRUE    |cloudaccountexternalid|                      |CT-Mg1-Mg1          |Colin-Turney-Azure-1/Colin-Azure-MgtGroup/CT-Mg1/CT-Mg1-Mg1/CT-Mg1-Mg1-Mg1|5         |Azure|
|CT-Mg2              |TRUE    |cloudaccountexternalid|                      |Colin-Azure-MgtGroup|Colin-Turney-Azure-1/Colin-Azure-MgtGroup/CT-Mg2                          |3         |Azure|
|CT-Mg2-Su1          |FALSE   |cloudaccountexternalid|                      |CT-Mg2              |Colin-Turney-Azure-1/Colin-Azure-MgtGroup/CT-Mg2/CT-Mg2-Su1               |4         |Azure|
|CT-Mg3              |TRUE    |cloudaccountexternalid|                      |Colin-Azure-MgtGroup|Colin-Turney-Azure-1/Colin-Azure-MgtGroup/CT-Mg3                          |3         |Azure|


#### Script 1: Output File 2: AD_OUTPUT_FILE.csv

|Group Name          |Wiz Project|Member Name           |Member UPN/Email        |Originating Cloud   |
|--------------------|-----------|----------------------|------------------------|--------------------|
|Wiz_ProjectName_ProjectReader|ProjectName|Colin Turney          |colin.turney@example.com|Azure               |


<!-- TOC --><a name="script-2-2-create_projectspy"></a>
## Script 2: 2-create_projects.py

The purpose of this script is to take an input CSV file in the same format as Script 1 - Output File 1, and create a project and folder project structure as prescribed within that file.

It will generate an Output file that lists all project names and each project's corresponding project ID that was created on Wiz.

<!-- TOC --><a name="script-2-how-to-run-the-script"></a>
### Script 2: How to run the script

It's recommended to ensure you have a Python virtualenv set up, using the `requirements.txt` file provided in this repository.

Make sure to create a Wiz Service Account with ONLY the following permission across all projects:
* Type: `Custom Integration (GraphQL API)`
* Project Scope: `All Projects`
* API Scope: `admin:projects, read:all`

Once loaded, create a wrapper bash script called `2-run.sh` or similar, structured similar to below:

```
export WIZ_CLIENT_ID="WIZ_CLIENT_ID"
export WIZ_CLIENT_SECRET="WIZ_CLIENT_SECRET"
export INPUT_FILENAME="INPUT_FILENAME"
export OUTPUT_FILENAME="OUTPUT_FILENAME"
export LOGGING_LEVEL="LOGGING_LEVEL"
export WIZ_DATACENTER="WIZ_DATACENTER"
export WRITE_MODE="WRITE_MODE"

python 2-create_projects.py "${WIZ_CLIENT_ID}" "${WIZ_CLIENT_SECRET}" "${INPUT_FILENAME}" "${OUTPUT_FILENAME}" "${LOGGING_LEVEL}" "${WIZ_DATACENTER}" "${WRITE_MODE}"

```

Where the [values] above align to as follows:

* WIZ_CLIENT_ID: The client id from the generated Wiz service account
* WIZ_CLIENT_SECRET: The client secret from the generated Wiz service account
* INPUT_FILENAME: The name of the input file being supplied to the script, residing in the same directory as the script.
* OUTPUT_FILENAME: The name of the output file that the script will write to, residing in the same directory as the script.
* LOGGING_LEVEL: A lower case string set to "debug", "info" "warning" "error" "critical". Leave unset to not set a logging level.
* WIZ_DATACENTER: A lower case string set to the name of the Wiz DC used by your tenant (e.g. eu7)
* WRITE_MODE: `True` or `False`, depending on whether you want the script to create/update projects on Wiz or not.

<!-- TOC --><a name="script-2-expected-output"></a>
### Script 2: Expected Output

The script will output one CSV file. 

#### Script 2: Output File: OUTPUT_FILENAME.csv

The output of this script will be as follows. This is a CSV detailing each project

The script will create an output file at the location specified. The output file will have the following structure:

```
Project ID, Project Name, Is Folder
"52aac7d7-67d7-54a3-8cdf-EXAMPLE","Colin-Turney-Test1","True"
"36ce525b-5418-597e-9b3c-EXAMPLE","Colin-Turney-Test1-FP1","True"
"1575fe5c-f475-5c83-9981-EXAMPLE","Colin-Turney-Test1-FP1-P1","False"
"f69c0835-1d44-5bdd-b903-EXAMPLE","Colin-Turney-Test1-FP1-FP1","True"
"b91d352a-2504-5c2d-8530-EXAMPLE","Colin-Turney-Test1-FP1-FP1-P1","False"
"445ef05c-01a5-56d8-8b52-EXAMPLE","Colin-Turney-Test1-FP2","True"
"1383ca1f-65be-592d-adc7-EXAMPLE","Colin-Turney-Test1-FP2-P1","False"
"7ffb2df0-143d-5b76-aed6-EXAMPLE","Colin-Turney-Test1-FP3","True"
```

|Project ID                     |Project Name                 |Is Folder|
|-------------------------------|-----------------------------|---------|
|52aac7d7-67d7-54a3-8cdf-EXAMPLE|Colin-Turney-Test1           |True     |
|36ce525b-5418-597e-9b3c-EXAMPLE|Colin-Turney-Test1-FP1       |True     |
|1575fe5c-f475-5c83-9981-EXAMPLE|Colin-Turney-Test1-FP1-P1    |False    |
|f69c0835-1d44-5bdd-b903-EXAMPLE|Colin-Turney-Test1-FP1-FP1   |True     |
|b91d352a-2504-5c2d-8530-EXAMPLE|Colin-Turney-Test1-FP1-FP1-P1|False    |
|445ef05c-01a5-56d8-8b52-EXAMPLE|Colin-Turney-Test1-FP2       |True     |
|1383ca1f-65be-592d-adc7-EXAMPLE|Colin-Turney-Test1-FP2-P1    |False    |
|7ffb2df0-143d-5b76-aed6-EXAMPLE|Colin-Turney-Test1-FP3       |True     |

The above fields have the following meanings:

* Project ID: The Project ID of the project that was created in Wiz.
* Project Name: The name of the project that was created in Wiz.
* isFolder: If the project that was created is a Folder Project or not.

<!-- TOC --><a name="script-3-3-extract_saml_mappingspy"></a>
## Script 3: 3-extract_saml_mappings.py

The purpose of this script is to take one CSV file as input: the `AD_OUTPUT_FILE` from Script 1, and then build a SAML role mappings table that maps the suggested SAML group names to their respective projects. 

It will generate an Output file that can then be provided as input to the Wiz SAML Role Mappings API recipe.

<!-- TOC --><a name="script-3-how-to-run-the-script"></a>
### Script 3: How to run the script

It's recommended to ensure you have a Python virtualenv set up, using the `requirements.txt` file provided in this repository.

No Wiz service account is required for this script- it just runs locally, taking one CSV file as input and outputting one CSV file.

Once loaded, create a wrapper bash script called `3-run.sh` or similar, structured similar to below:

```
export ADGROUPS_INPUT_FILE="ADGROUPS_INPUT_FILE"
export SAML_MAPPINGS_OUTPUT_FILE="SAML_MAPPINGS_OUTPUT_FILE"
export DEFAULT_SAML_ROLE="DEFAULT_SAML_ROLE"
export LOGGING_LEVEL="LOGGING_LEVEL"

python 3-extract_saml_mappings.py "${ADGROUPS_INPUT_FILE}" "${SAML_MAPPINGS_OUTPUT_FILE}" "${DEFAULT_SAML_ROLE}" "${LOGGING_LEVEL}"

```

Where the [values] above align to as follows:

* ADGROUPS_INPUT_FILE: The AD groups file given as output from Script 1.
* SAML_MAPPINGS_OUTPUT_FILE: The name of a file to be produced as output from this script, for latter use with the Wiz SAML Role Mappings API recipe.
* DEFAULT_SAML_ROLE: The Wiz Role name to be applied (e.g. `ProjectReader`)
* LOGGING_LEVEL: A lower case string set to "debug", "info" "warning" "error" "critical". Leave unset to not set a logging level.

<!-- TOC --><a name="script-3-expected-output"></a>
### Script 3: Expected Output

The script will output one CSV file. 

#### Script 3: Output File: SAML_MAPPINGS_OUTPUT_FILE.csv

The output of this script will be as follows. This is a CSV detailing each project

The script will create an output file at the location specified. The output file will have the following structure:

```
SAML Group Name,Permissions,Project Name
"Wiz_ProjectName_ProjectReader","ProjectReader","ProjectName"

```

|SAML Group Name              |Permissions  |Project Name|
|-----------------------------|-------------|------------|
|Wiz_ProjectName_ProjectReader|ProjectReader|ProjectName |


The above fields have the following meanings:

* SAML Group Name: The name of the SAML group from the SSO provider
* Permissions: The Wiz Permission scope to be applied to this SAML group
* Project Name: The Name of the Wiz projects that this permission scope and SAML group is applied to.
