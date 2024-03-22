# Wiz Cleanup and Archive Projects Script

# Disclaimer - PLEASE READ

By using this software and associated documentation files (the “Software”) you hereby agree and understand that:

1. The use of the Software is free of charge and may only be used by Wiz customers for its internal purposes.
2. The Software should not be distributed to third parties.
3. The Software is not part of Wiz’s Services and is not subject to your company’s services agreement with Wiz.
4. THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL WIZ BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE USE OF THIS SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Description

The aim of this script is to, in bulk, run an update operation on all projects descending from defined root project id. The update operation will perform the following:
    * Add a pre-defined suffix to the project name.
    * Add a pre-defined suffix to the project slug.
    * Set the project to archived or unarchived, as defined in the script's parameters.


# How to run the script

It's recommended to ensure you have a Python virtualenv set up, using the `requirements.txt` file provided in this repository.

Make sure to create a Wiz Service Account with ONLY the following permission across all projects:
* Type: `Custom Integration (GraphQL API)`
* Project Scope: `All Projects`
* API Scope: `read:all, read:projects, admin:projects`

Once loaded, create a wrapper shell script called `cap_run.sh` or similar, structured similar to below:

```

export CLIENT_ID="CLIENT_ID"
export CLIENT_SECRET="CLIENT_SECRET"
export ROOT_PROJECT_ID="ROOT_PROJECT_ID"
export TARGET_ARCHIVED="true"
export PROJECT_NAME_SUFFIX="_OLD"
export SLUG_SUFFIX="-old" #Only alphanumeric and dashes are permitted here
export SET_ARCHIVE_STATUS="true"
export LOGGING_LEVEL="info"
export WIZ_DATACENTER="us20"
export WRITE_MODE="True"

python cleanup_archive_projects.py "${WIZ_CLIENT_ID}" "${WIZ_CLIENT_SECRET}" "${ROOT_PROJECT_ID}" "${TARGET_ARCHIVED}" "${PROJECT_NAME_SUFFIX}" "${SLUG_SUFFIX}" "${SET_ARCHIVE_STATUS}" "${LOGGING_LEVEL}" "${WIZ_DATACENTER}" "${WRITE_MODE}"

```

Where the [values] above align to as follows:

* WIZ_CLIENT_ID: The client id from the generated Wiz service account
* WIZ_CLIENT_SECRET: The client secret from the generated Wiz service account
* ROOT_PROJECT_ID: The id of the Wiz project which should be archived, renamed and reslugged along with it's children.
* TARGET_ARCHIVED: Set whether already-archived projects should be updated by the script. [true or false]
* PROJECT_NAME_SUFFIX: The suffix to add to each project name
* SLUG_SUFFIX: The suffix to add to each slug [only alphanumeric and dashes are permitted here]
* SET_ARCHIVE_STATUS: The is_archived value to update each project to [true or false]
* LOGGING_LEVEL: A lower case string set to "debug", "info" "warning" "error" "critical". Leave unset to not set a logging level.
* WIZ_DATACENTER: A lower case string set to the name of the Wiz DC used by your tenant (e.g. eu7)
* WRITE_MODE: `True` or `False`, depending on whether you want the script to update projects on Wiz.