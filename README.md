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

## Design helper

The design_helpers.py script queries the workspaces available and gets the users choice of workspace, as well as querying the projects in the workspace and gets the users choice of project they want to use. 

This script cant be executed by itself as it holds only functions and queries. The purpose of this script is to be used as an addition to any script that queries the design API, as most scripts will need to get the workspace and project the user wants to use. 

## Comments

The project_comments.py example uses multiple queries that requests a token as an input, as well as a workspace and project from the user. It will then return all comments from that project.

`python project_comments.py`

When the script is executed, it will request an input for the token to make requests to the API. After the token is provided, the first query returns all available workspaces. The user then needs to pick the workspace they want to request to. It will then take the workspace URL for the workspace the user chose and use that in the second query, which lists all projects in that workspace with an index value next to it. This allows the user to type in the index value of which project they wish to view, rather than typing in the workspace. When an index value is passed into the script, the third query will print all comments in that project with the comment thread number, comment thread ID, comment ID, the username of who created the comment, the time that the comment was created at, and the text in the comment. If the comment has been modified, it will display the username of who modified the comment and what time is was modified. 

## Changing Comments

The project_change_comments.py example is similar to the project_comments.py example, however after returning all the comments for a particular project, it will allow the user to update, create or delete a comment within the project that they chose.

`python project_change_comments.py`

When the script is executed, it will nearly the same as project_comments.py. There difference is that it will then ask the user to input 1, 2 or 3 which correspond to update, create or delete a comment. 
If the user chose 1, which is update, it will then ask the user to input the comment ID of the comment they want to alter. Then it will ask the user to input text of what they want the comment to say. The script will then get the comment thread ID that the comment ID is in and run a mutation which will update the comment to display the text they have entered. 
If the user chose 2, which is create a comment, the user is required to enter the comment thread ID of which section they want to add a comment to as well as the text they want the comment to say. Then the script will run a mutation to create a comment in the comment thread ID location the user entered with the text they entered. 
If the user chose 3, they will be asked to enter the comment ID for the comment they want to delete. The script will then get the comment thread ID that the comment ID is in, then run a mutation to delete the comment. 

## Design components

The project_design_components.py example uses multiple queries that takes a token input and returns all available workspaces, then takes the users choice of which workspace to use as an input and returns all projects in the workspace. It then takes the users input again for a choice of project and returns the first 25 components used for a project.

`python project_design_components.py`

When this script is executed, it will first ask the user to input a token. It will then use this token to query to the API all available workspaces and return them in a list to the user with an index value. The user will then choose a workspace by selecting the index value next to the workspace. If they choose a workspace that is not listed, the script will loop until a valid workspaces is chosen. Once a valid workspace is chosen, the script will use this workspace to query to the API all available projects in this workspace. It will then display all available projects with an index value. The user then needs to choose a project by selecting the index value next to the project they want to retrieve information from. If an invalid project is chosen, the script will loop until a valid project is chosen. After a valid project is chosen, the project ID is used to query the API to retrieve the first 25 components used in the project, along with its designator, name, comment, and description. If a component also has parameters, it will also display the parameters name and value. In this particular example, only the first variant is used so the query will only return information about the first variant.

## Design paging

The design_paging.py example queries the design API for components used in a project chosen by the user. It will then print a limited amount of components in pages. 

`python design_paging.py`

When the script is executed, it will print all available workspaces. Then the user will need to choose which workspace they want to use. This is then repeated for projects. After the user has chosen the workspace and project, a list of components in the project are printed in pages. The page size is set to four, but can be changed, so the list printed is four long. The script will then allow the user to pick either next page, previous page or exit by selecting the number assigned next to the choices. 
If the user chooses 1, which is next page, the script will print the next four components. However, if the user chooses next page when there are no more components to print, it will ask the user to choose a different option. 
If the user chooses 2, which is previous page, the script will print the previous four components. If there is no previous page, the user is asked to input a different option. 
If the user chooses 3, which is exit, the script will stop. 

## Supply paging

The supply_paging.py example queries the supply API for all available parts. It will then display those parts in pages in limited amounts. The user can then change which page they are viewing. 

`python supply_paging.py`

When the script is executed, the user is asked for a token input. Then the user is asked to enter a part MPN. This MPN doesn't need to be an exact MPN as it is used to search through the database to find similar MPNs. The MPN and token is then used to query the supply API. The MPN entered is searched for and the query returns all possible part results that are similar to the MPN the user entered. However, the number of matched parts may be very large, so the results are limited to 10 at a time. Then the script is similar to design paging. It will ask the user to choose next page, previous page or exit to change the page of results displayed or exit the program. However, this script has a fourth option, the user is able to choose a page to visit, rather then choosing next page until they reach the page they want to visit. This option will request the user to input a page they want to visit. If this page doesn't exist or the number they choose is out of range, it will return invalid page number. If the page does exist, it will query the Supply API from the page number.

## Supply filter

The supply_filter.py example quries the supply API for the first 10 parts which include the filter.

`python supply_filtering_and_sorting.py`

When the script is executed, the user is asked for a token input. It will then ask the user to query the supply API by choosing either filter or by sort by entering the index value assigned to it. The attribute that is used for filtering or sorting will be the same and is declared as a global variable. This global variable can be changed for another filtering item.
Next, the script runs a query to get the list of attributes that can be used for filtering or sorting and displays these to the user. If the user chose filtering, there is an additional option where they can enter their own value to search for. The user is prompted to choose one by providing the index. If the user chose to filter, they will be prompted to enter an attribute value to filter to. If the user then chose to enter their own value, they will be asked to enter their own value. If instead the user chose to sort, they will be prompted to choose a sort direction: ascending or descending.
The script will run a second query to get the parts. If the user chose to filter, they will be filtered according to the provided attribute value, either pre determined values or the users own value. If the user chose to sort, the parts will be sorted according to the chosen sort direction. The query is limited to return 10 parts. The script will print out the amount of hits and, for each part, the part name, category, manufacturer, MPN, average number of parts available, description, median price, currency, and the names and values of attributes used for sorting or filtering.
The attribute used for filtering or sorting can be changed at the top of the script. In a real application, multiple filters can be used at once, and filtering can be combined with sorting.
