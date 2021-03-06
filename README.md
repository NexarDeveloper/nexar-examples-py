# nexar-examples-py
Various example Nexar queries to use as inspiration for developing custom partner applications

## Obtaining Tokens
Each example in this repository will require an access token. Tokens can be generated by using the print_token.py program from the nexar-token-py repository:

`python print_token.py <client_id> <client_secret> supply.domain`

`python print_token.py <client_id> <client_secret> user.access design.domain`

The client_id and client_secret fields are found within the application details section from https://nexar.com/applications. The "supply.domain" scope is for applications that use queries prefixed with "sup" while "design.domain" (usually with "user.access" included) is for applications that require an Altium workspace resource used by queries/mutations that are prefixed with "des". The "design.domain" token will require an additional step in the authorization process that will open a web browser page to collect username and password credentials for the Altium workspace.

We recommend capturing the output from these programs in a shell variable for use with these example programs.  The token can be used as part of the command line arguments as shown here:

`python workspace_info.py -t $token <name>`

The primary advantage of capturing the token in a shell variable is the ability to re-use the token for multiple runs of these examples without having to regenerate the token for each invocation. Tokens may also be generated directly in the code using the nexar-token-py repository by importing it as a submodule/subtree and adding the following to your application:

`from nexar_module.nexar_token import get_token`

and then calling the get_token function with the required credentials (see the README file in the nexar-token-py repository for details).

All tokens are time limited (typically for 24 hours) and new tokens will be needed after expiration.

## Nexar queries
All Nexar queries are based on the GraphQL query language.  The examples in this repository typically begin by defining a query string and then calling a Nexar client with that string and some variable definitions to target the query to a specific dataset.  For more information about the GraphQL language please visit https://graphql.org.  For information about the structure of the Nexar schema please visit https://api.nexar.com/ui/voyager.

## A simple part search
The mpn_info.py example queries for information related to a manufacturers part number (MPN):

`python mpn_info.py -t $token <mpn>`

Since this example uses only supply scope data (queries prefixed with "sup") the get_token/print_token.py generator should be used for a token that must include the scope for "supply.domain". The output will be similar to this:

\{\
 "results": \[\
  \{\
   "part": \{\
    "category": \{\
     "parentId": "4850",\
     "id": "4858",\
     "name": "Signal Relays",\
     "path": "/electronic-parts/electromechanical/relays/signal-relays"\
    \},\
    "mpn": "1-1415898-1",\
    "manufacturer": \{\
     "name": "TE Connectivity / AMP"\
    \},\
    "shortDescription": "Electromechanical Relay 48VDC 5.52KOhm 16A SPST-NO (29x12.7x15.7)mm THT Power Relay",\
    "descriptions": \[\
...

The output is a string dump of the JSON structure returned by the Nexar query.  The content of this structure can be customized by editing the string QUERY_MPN in the source code.  Try adding or removing fields to this query to observe the effect on the returned structure.

## Advanced part searching

The mpn_pricing_to_csv.py is a more sophisticated example of using Nexar to request information from multiple part numbers (MPN) with a single query:

`python mpn_pricing_to_csv.py -t $token <mpn> <second mpn> <third mpn> ...`

The query resuts are then processed into a csv output meant to display a table of distributors and prices for each mpn.

## A365 workspace details
The workspace_info.py example is a simple query of an Altium A365 workspace with the workspace name given as the required argument:

`python workspace_info.py -t $token <name>`

Since this example uses A365 resources the get_token/print_token.py generator should be used with the "design.domain" scope (a typcially token would also include "user.access" and even "supply.domain" if part queries are to be included). The output will be similar to this:

\[\
 \{\
  "url": "https://nexar-demo.365.altium.com/", \
  "name": "Nexar Demo",\
  "description": "This workspace is configured to support demonstrations of A365/Nexar to Altium partners",\
  "projects": \[\
   \{\
    "id": "RGVzUHJvamVjdApkaHR0cHM6Ly9uZXhhci1kZW1vLjM2NS5hbHRpdW0uY29tL3wyMzRCNkQ1My1GOTNELTRERDAtOTgxNS0yRkJBMEVEQUVDN0U=",\
    "name": "Kame-1",\
    "description": "Complete multi-board Kame Drone device assembly."\
   \},\
   \{\
    "id": "RGVzUHJvamVjdApkaHR0cHM6Ly9uZXhhci1kZW1vLjM2NS5hbHRpdW0uY29tL3w0MEFCRjIxOS1BRjM0LTRENzYtQTQ5OC1ENDI2OURDMjQ1MUM=",\
    "name": "Kame_FMU - Copy to demo progress",\
    "description": "Managed project cloned from Kame_FMU"\
   \},\
...

The content returned from the workspace may be easily tailored by editing the query string in the example code. Please pay particular attention to the "id" field within "projects" as this id will be used for several of the project related examples.

## Examining the BOM from an A365 project
The project_BOM.py example is a query that uses the project id to identify the BOM source in the A365 workspace:

`python workspace_info.py -t $token <project_id>`

The project id is static across Nexar sessions and contains all of the information needed to identify the correct workspace and design data.  This example is important to inspect to understand how the Nexar query can be used to get design information from either the current version of the design (labeled workInProgress in our schema) or from a specific version labeled for a release.  Additionally, each design may contain variants that will be a unique configuration of the design components.

## Supply token caching

The supply_token_caching_script.py example uses multiple manufacturer part numbers (MPN) in a single query, to retrieve information about specific parts, similar to mpn_pricing_to_csv.py, however it will cache the access token in a file called tokenCache.json. In this case, caching in a file is more useful than caching in memory,  because the script is not a long-lived application but it could still be run many times in one day. Using a cached access token reduces the burden on Nexar servers.

`python supply_token_caching_script.py <mpn> <second mpn> <third mpn> ...`

During execution, the program checks for a json file containing an access token with an expiry time. If this doesn't exist, it will create the json file for this. This json file will cache the access token and expiry time. This will be valid for a set time. Then is makes a query using the access token and returns the query and the script ends. Once the script is executed again, it will check if the json file exists. If it does exists, instead of requesting another token, it will compare the expiry time of the access token with the current time. If it has not passed the expiry time, the access token is reused. If it has passed the expiry time, the access token is invalid and another access token is created and cached in the json file with its expiry time, overwriting the previous access token stored in the json file as well as the expiry time. The query results are then processed into a csv output meant to display a table of distributors and prices for each mpn.

### Requirements:
requests

A `NEXAR_CLIENT_ID` and `NEXAR_CLIENT_SECRET` environment variables are needed to be set in system properties as they are needed to run the script.


## Regionalization 

The design_regionalization.py example uses multiple queries that initially takes the user token as an input for the first query, then a second query takes another user input to choose a Nexar server that is located geographically close to an Altium 365 workspace.

`python design_regionalization.py`

Once the script is executed, it will request an input for the token to make requests to the API. Once the token is provided, the query returns the name of the location and the Url. It will then display each possible location with an index as well as an input prompt. The user then needs to input the index assigned to the location they want to request to. The purpose of this part of the script is to reduce latency (faster queries). After the user provides an index value, the script sends the second query to the location chosen by the user.


## Comments

The project_comments.py example uses multiple queries that requests a token as an input, as well as a project from the user. It will then return all comments from that project, the title of the project and the username of who created the comment.

`python project_comments.py`

When the script is executed, it will request an input for the token to make requests to the API. After the token is provided, the first query returns all available workspaces. The script chooses the first workspace in the list. It will then take the workspace URL and use that in the second query, which lists all projects in that workspace with an index value next to it. This allows the user to type in the index value of which project they wish to view, rather than typing in the workspace. When an index value is passed into the script, the third query will print all comments in that project with the comment thread number and the username of who created the comment.

## Changing Comments

The project_change_comments.py example is similar to the project_comments.py example, however after returning all the comments for a particular project, it will allow the user to update, create or delete a comment within the project that you chose.

`python project_change_comments.py`

When the script is executed, it will run exactly the same as project_comments.py, however, after displaying all of the comments, it will then ask the user to input 1, 2 or 3 which correspond to update, create or delete a comment. 
If the user chooses 1, which is update, it will then ask the user to input the comment ID of the comment they want to alter. Then it will ask the user to input text of what they want the comment to say. The script will then get the comment thread ID that the comment ID is in and run a mutation which will update the comment to display the text they have entered. 
If the user chose 2, which is create a comment, the user is required to enter the comment thread ID of which section they want to add a comment to as well as the text they want the comment to say. Then the script will run a mutation to create a comment in the comment thread ID location the user entered with the text they entered. 
If the user chose 3, they will be asked to enter the comment ID for the comment they want to delete. The script will then get the comment thread ID that the comment ID is in, then run a mutation to delete the comment. 

## Design components

The project_design_components.py example uses multiple queries that takes a token input and returns all available workspaces, then takes the users choice of which workspace to use as an input and returns all projects in the workspace. It then takes the users input again for a choice of project and returns the first 25 components used for a project.

`python project_design_components.py`

When this script is executed, it will first ask the user to input a token. It will then use this token to query to the API all available workspaces and return them in a list to the user with an index value. The user will then choose a workspace by selecting the index value next to the workspace. If they choose a workspace that is not listed, the script will loop until a valid workspaces is chosen. Once a valid workspace is chosen, the script will use this workspace to query to the API all available projects in this workspace. It will then display all available projects with an index value. The user then needs to choose a project by selecting the index value next to the project they want to retrieve information from. If an invalid project is chosen, the script will loop until a valid project is chosen. After a valid project is chosen, the project ID is used to query the API to retrieve the first 25 components used in the project, along with its designator, name, comment, and description. If a component also has parameters, it will also display the parameters name and value. In this particular example, only the first variant is used so the query will only return information about the first variant.
