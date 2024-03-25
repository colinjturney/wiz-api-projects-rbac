# Wiz Recipe Folder Projects

# Disclaimer - PLEASE READ

By using this software and associated documentation files (the “Software”) you hereby agree and understand that:

1. The use of the Software is free of charge and may only be used by Wiz customers for its internal purposes.
2. The Software should not be distributed to third parties.
3. The Software is not part of Wiz’s Services and is not subject to your company’s services agreement with Wiz.
4. THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL WIZ BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE USE OF THIS SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Description

The aim of this script is to take a CSV as input which specifies the names of projects that should be created in Wiz together with their linked cloud account IDs, whether they are folder projects and their parent project name if applicable.

Please read this README and the FAQs carefully.

## FAQs

1. **Does it matter in which order the projects are listed in the input file?**<br/>
 **YES** it does. Parent projects *MUST* be specified in the CSV input prior to their child project being specified, or should exist in the Wiz portal first.

1. **What happens if the script is interrupted part-way-through?**<br/>
It should exit gracefully and still list in the output CSV file the details of projects that were successfully created. If this happens, the output file should be copied and retained. It should then be possible to rerun the script again with the same input file.

1. **Can the script be used to update projects that have already been created?**
This should be possible, although the project names would have to match- i.e. you want to update the project's parentage, cloud account links or cloud organization links.

# How to run the script

It's recommended to ensure you have a Python virtualenv set up, using the `requirements.txt` file provided in this repository.

Make sure to create a Wiz Service Account with ONLY the following permission across all projects:
* Type: `Custom Integration (GraphQL API)`
* Project Scope: `All Projects`
* API Scope: `read:all, read:projects, admin:projects`

Once loaded, create a wrapper shell script called `cap_run.sh` or similar, structured similar to below:

```

export WIZ_CLIENT_ID="WIZ_CLIENT_ID"
export WIZ_CLIENT_SECRET="WIZ_CLIENT_SECRET"
export INPUT_FILENAME="INPUT_FILENAME"
export OUTPUT_FILENAME="OUTPUT_FILENAME"
export LOGGING_LEVEL="LOGGING_LEVEL"
export WIZ_DATACENTER="WIZ_DATACENTER"
export WRITE_MODE="WRITE_MODE"

python recipe_folder_projects.py "${CLIENT_ID}" "${CLIENT_SECRET}" "${INPUT_FILENAME}" "${OUTPUT_FILENAME}" "${LOGGING_LEVEL}" "${WIZ_DATACENTER}" "${WRITE_MODE}"

```

Where the [values] above align to as follows:

* WIZ_CLIENT_ID: The client id from the generated Wiz service account
* WIZ_CLIENT_SECRET: The client secret from the generated Wiz service account
* INPUT_FILENAME: The name of the input file being supplied to the script, residing in the same directory as the script.
* OUTPUT_FILENAME: The name of the output file that the script will write to, residing in the same directory as the script.
* LOGGING_LEVEL: A lower case string set to "debug", "info" "warning" "error" "critical". Leave unset to not set a logging level.
* WIZ_DATACENTER: A lower case string set to the name of the Wiz DC used by your tenant (e.g. eu7)
* WRITE_MODE: `True` or `False`, depending on whether you want the script to create/update projects on Wiz.

# Input and Output Files

## Input File

The script takes a CSV file as input, which should follow the structure below:

```
wiz-project-name,isFolder,cloudAccountLinks,cloudOrganizationLinks,parentProjectName
Colin-Turney-Test1,TRUE,,,
Colin-Turney-Test1-FP1,TRUE,,,Colin-Turney-Test1
Colin-Turney-Test1-FP1-P1,FALSE,,r-21pn,Colin-Turney-Test1-FP1
Colin-Turney-Test1-FP1-FP1,TRUE,,,Colin-Turney-Test1-FP1
Colin-Turney-Test1-FP1-FP1-P1,FALSE,142956687879,,Colin-Turney-Test1-FP1-FP1
Colin-Turney-Test1-FP2,TRUE,,,Colin-Turney-Test1
Colin-Turney-Test1-FP2-P1,FALSE,053334765486,,Colin-Turney-Test1-FP2
Colin-Turney-Test1-FP3,TRUE,,,Colin-Turney-Test1
```

Below is a tablular representation of this structure.

|wiz-project-name             |isFolder|cloudAccountLinks|cloudOrganizationLinks|parentProjectName         |
|-----------------------------|--------|-----------------|----------------------|--------------------------|
|Colin-Turney-Test1           |TRUE    |                 |                      |                          |
|Colin-Turney-Test1-FP1       |TRUE    |                 |                      |Colin-Turney-Test1        |
|Colin-Turney-Test1-FP1-P1    |FALSE   |                 |r-21pn                |Colin-Turney-Test1-FP1    |
|Colin-Turney-Test1-FP1-FP1   |TRUE    |                 |                      |Colin-Turney-Test1-FP1    |
|Colin-Turney-Test1-FP1-FP1-P1|FALSE   |142956687879     |                      |Colin-Turney-Test1-FP1-FP1|
|Colin-Turney-Test1-FP2       |TRUE    |                 |                      |Colin-Turney-Test1        |
|Colin-Turney-Test1-FP2-P1    |FALSE   |053334765486     |                      |Colin-Turney-Test1-FP2    |
|Colin-Turney-Test1-FP3       |TRUE    |                 |                      |Colin-Turney-Test1        |

The above fields have the following meanings:

* wiz-project-name: The UNIQUE name of the project to create in Wiz. Note, all projects to be created must have UNIQUE names.
* isFolder: If the project to be created is a folder project or a standard project. If it is a folder project, it should NOT contain cloudAccountLinks or cloudOrganizationLinks
* cloudAccountLinks: The externalID(s) of cloud subscriptions to be included in this project
* cloudOrganizationLinks: The externalID(s) of cloud organizatinos to be included in this project.
* parentProjectName: The name of the parent project that this project will be a child project of.

## Output File

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