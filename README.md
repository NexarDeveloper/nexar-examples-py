# nexar-examples-py

Various example Nexar queries to use as inspiration for developing custom partner applications. All of the examples are powered by one of the Nexar clients which can be found in `examplePrograms/nexarClients`. These classes provide the necessary functionality to fetch tokens and then query the API.

## Prerequisites

Before using any of these examples you will need to have a Nexar account, if you don't you can sign up at [Nexar](https://www.nexar.com).

For the supply data queries, you will need to have a Nexar application with the supply scope.

For the design data queries (Altium 365 data), you will need to have a Nexar application with the design scope as well as having an Altium 365 workspace.

With the client credentials of your chosen application set the environment variables `NEXAR_CLIENT_ID` and `NEXAR_CLIENT_SECRET`.

## Nexar queries

All Nexar queries are based on the GraphQL query language. The examples in this repository typically begin by defining a query string and then calling a Nexar client with that string and some variable definitions to target the query to a specific dataset. For more information about the GraphQL language please visit https://graphql.org. For information about the structure of the Nexar schema please visit https://api.nexar.com/ui/voyager.

## A simple part search

The `mpn_info.py` example queries for information related to a manufacturers part number (MPN):

```
python mpn_info.py
```

The output is a string dump of the JSON structure returned by the Nexar query. The content of this structure can be customized by editing the string QUERY_MPN in the source code. Try adding or removing fields to this query to observe the effect on the returned structure.

## Advanced part searching

The mpn_pricing_to_csv.py is a more sophisticated example of using Nexar to request information from multiple part numbers (MPN) with a single query:

```
python mpn_pricing_to_csv.py
```

The query resuts are then processed into a csv output meant to display a table of distributors and prices for each mpn.

## A365 workspace details

The workspace_info.py example is a simple query of an Altium A365 workspace:

```
python workspace_info.py
```

The content returned from the workspace may be easily tailored by editing the query string in the example code. Please pay particular attention to the "id" field within "projects" as this id will be used for several of the project related examples.

## Examining the BOM from an A365 project

The project_BOM.py example is a query that uses the project id to identify the BOM source in the A365 workspace:

```
python workspace_info.py
```

The project id is static across Nexar sessions and contains all of the information needed to identify the correct workspace and design data. This example is important to inspect to understand how the Nexar query can be used to get design information from either the current version of the design (labeled workInProgress in our schema) or from a specific version labeled for a release. Additionally, each design may contain variants that will be a unique configuration of the design components.

## Regionalization

The design_regionalization.py example uses multiple queries, the first of which to get the locations and URLs, then a second query takes another user input to choose a Nexar server that is located geographically close to an Altium 365 workspace.

```
python design_regionalization.py
```

Once the script is executed, it will query for the name of the location and the URL. It will then display each possible location with an index as well as an input prompt. The user then needs to input the index assigned to the location they want to request to. The purpose of this part of the script is to reduce latency (faster queries). After the user provides an index value, the script sends the second query to the location chosen by the user.

## Comments

The project_comments.py example uses multiple queries that request a workspace and project from the user as an input. It will then return all comments from that project.

```
python project_comments.py
```

The first query returns all available workspaces. The user then needs to pick the workspace they want to request to. It will then take the workspace URL for the workspace the user chose and use that in the second query, which lists all projects in that workspace with an index value next to it. This allows the user to type in the index value of which project they wish to view, rather than typing in the workspace. When an index value is passed into the script, the third query will print all comments in that project with the comment thread number, comment thread ID, comment ID, the username of who created the comment, the time that the comment was created at, and the text in the comment. If the comment has been modified, it will display the username of who modified the comment and what time is was modified.

## Changing Comments

The project_change_comments.py example is similar to the project_comments.py example, however after returning all the comments for a particular project, it will allow the user to update, create or delete a comment within the project that they chose.

```
python project_change_comments.py
```

When the script is executed, it will nearly be the same as project_comments.py. The difference is that it will then ask the user to input 1, 2 or 3 which correspond to update, create or delete a comment.
If the user choses 1, which is update, it will then ask the user to input the comment ID of the comment they want to alter. Then it will ask the user to input text of what they want the comment to say. The script will then get the comment thread ID that the comment ID is in and run a mutation which will update the comment to display the text they have entered.
If the user choses 2, which is create a comment, the user is required to enter the comment thread ID of which section they want to add a comment to as well as the text they want the comment to say. Then the script will run a mutation to create a comment in the comment thread ID location the user entered with the text they entered.
If the user choses 3, they will be asked to enter the comment ID for the comment they want to delete. The script will then get the comment thread ID that the comment ID is in, then run a mutation to delete the comment.

## Design components

The project_design_components.py example uses multiple queries that return all available workspaces, then takes the user's choice of which workspace to use as an input and returns all projects in the workspace. It then takes the user's input again for a choice of project and returns the first 25 components used for a project.

```
python project_design_components.py
```

When this script is executed, it will query to the API all available workspaces and return them in a list to the user with an index value. The user will then choose a workspace by selecting the index value next to the workspace. If they choose a workspace that is not listed, the script will loop until a valid workspaces is chosen. Once a valid workspace is chosen, the script will use this workspace to query to the API all available projects in this workspace. It will then display all available projects with an index value. The user then needs to choose a project by selecting the index value next to the project they want to retrieve information from. If an invalid project is chosen, the script will loop until a valid project is chosen. After a valid project is chosen, the project ID is used to query the API to retrieve the first 25 components used in the project, along with its designator, name, comment, and description. If a component also has parameters, it will also display the parameters name and value. In this particular example, only the first variant is used so the query will only return information about the first variant.

## Design paging

The design_paging.py example queries the design API for components used in a project chosen by the user. It will then print a limited amount of components in pages.

```
python design_paging.py
```

When the script is executed, it will print all available workspaces. Then the user will need to choose which workspace they want to use. This is then repeated for projects. After the user has chosen the workspace and project, a list of components in the project are printed in pages. The page size is set to four, but can be changed, so the list printed is four long. The script will then allow the user to pick either next page, previous page or exit by selecting the number assigned next to the choices.
If the user chooses 1, which is next page, the script will print the next four components. However, if the user chooses next page when there are no more components to print, it will ask the user to choose a different option.
If the user chooses 2, which is previous page, the script will print the previous four components. If there is no previous page, the user is asked to input a different option.
If the user chooses 3, which is exit, the script will stop.

## Supply paging

The supply_paging.py example queries the supply API for all available parts. It will then display those parts in pages in limited amounts. The user can then change which page they are viewing.

```
python supply_paging.py
```

When the script is executed, the user is asked to enter a part MPN. This MPN doesn't need to be an exact MPN as it is used to search through the database to find similar MPNs. The MPN is then used to query the supply API. The MPN entered is searched for and the query returns all possible part results that are similar to the MPN the user entered. However, the number of matched parts may be very large, so the results are limited to 10 at a time. Then the script is similar to design paging. It will ask the user to choose next page, previous page or exit to change the page of results displayed or exit the program. However, this script has a fourth option, the user is able to choose a page to visit, rather then choosing next page until they reach the page they want to visit. This option will request the user to input a page they want to visit. If this page doesn't exist or the number they choose is out of range, it will return invalid page number. If the page does exist, it will query the Supply API from the page number.

## Supply filter

The supply_filter.py example queries the supply API for the first 10 parts which include the filter.

```
python supply_filtering_and_sorting.py
```

When the script is executed, it will ask the user to query the supply API by choosing either filter or by sort by entering the index value assigned to it. The attribute that is used for filtering or sorting will be the same and is declared as a global variable. This global variable can be changed for another filtering item.
Next, the script runs a query to get the list of attributes that can be used for filtering or sorting and displays these to the user. If the user chose filtering, there is an additional option where they can enter their own value to search for. The user is prompted to choose one by providing the index. If the user chose to filter, they will be prompted to enter an attribute value to filter to. If the user then chose to enter their own value, they will be asked to enter their own value. If instead the user chose to sort, they will be prompted to choose a sort direction: ascending or descending.
The script will run a second query to get the parts. If the user chose to filter, they will be filtered according to the provided attribute value, either pre determined values or the user's own value. If the user chose to sort, the parts will be sorted according to the chosen sort direction. The query is limited to return 10 parts. The script will print out the amount of hits and, for each part, the part name, category, manufacturer, MPN, average number of parts available, description, median price, currency, and the names and values of attributes used for sorting or filtering.
The attribute used for filtering or sorting can be changed at the top of the script. In a real application, multiple filters can be used at once, and filtering can be combined with sorting.

## Library components filtering

The filtered_library_components_to_csv.py example queries the design API for components in a workspace and writes certain components to a CSV file, depending on the user's choice of filter.

`python filtered_library_components_to_csv.py`

When the script is executed, it will query the design API and return components used in a workspace. The number of results can be quite large so by default, the limit of returned results is 10. The script then asks the user to input the index of what type of filter they want to apply to the returned components.
If the user chose 1, then no filter will be applied to the returned components, therefore it writes all of the components to a CSV file. Otherwise, if the user didn't choose 4, they are asked to enter the name of the parameter and the value of the parameter to filter for.
If the user chose 2, the list of components will be filtered to only include those components where the component's parameter value is equal to the specified value.
If the user chose 3, the list of components will be filtered to only include those components where the component's parameter value is not equal to the specified value.
If the user chose 4, the list of components will be filtered to only include those components where the component's parameter value starts with the specified value.
It will then write the returned part information to the CSV file called "library_components.csv". If this doesn't exist, it will create it. If the file already has information in it, the script will write over it.
