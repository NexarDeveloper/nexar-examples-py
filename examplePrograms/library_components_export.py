from nexarClients.design.nexarDesignClient import NexarClient
import os
import json
import csv

workspace_url = "Your workspace URL here"

# This is the API query, feel free to chop and change this to suit your use case.
# We recommend building queries in an IDE such as BananaCakePop or Postman.
# You can use BananaCakePop in a browser here: https://api.nexar.com/graphql/

graphql_query = '''query library ($workspaceURL: String!, $after: String) {
  desLibrary (workspaceUrl: $workspaceURL) {
    components (first: 100, after: $after) {
      totalCount
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        id
        folder {
          name
        }
        description
        name
        comment
        details {
          parameters {
            name
            value
          }
        }
        manufacturerParts {
          partNumber
          companyName
        }
      }
    }
  }
}'''


if __name__ == "__main__":

    # You will need to set your Nexar application's client ID and secret in your environment variables.
    # For this example, the application should have the design scope enabled.
    # Alternatively, switch how these are inputted but be careful not to share your credentials.

    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]

    # This class provides the necessary functionality to fetch access tokens and query the API.
    # The scopes provided allow us to query Altium 365 design data.

    nexar = NexarClient(client_id, client_secret, ["design.domain", "openid", "user.access"])

    def retrieve_components():
        page_info = {"hasNextPage": True, "endCursor": None}
        components = []
        while page_info["hasNextPage"]:
            variables = {
                "workspaceURL": workspace_url,
                "after": page_info["endCursor"]
            }
            response = nexar.get_query(graphql_query, variables)
            components += response["desLibrary"]["components"]["nodes"]
            page_info = response["desLibrary"]["components"]["pageInfo"]
            print("Retrieved", len(components), "components...")

        print("Retrieved", len(components), "components.")
        return components

    def json_export(components):
        with open("altium_library_components.json", "w") as json_file:
            json.dump(components, json_file)

    def csv_export(components):
        with open("altium_library_components.csv", "w", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=[
                # These are the headers for the file
                "Item ID",
                "Name",
                "Type",
                "Description",
                "RoHS Compliant",
                "Manufacturer 1",
                "Partnumber 1",
                "Manufacturer 2",
                "Partnumber 2",
                "Manufacturer 3",
                "Partnumber 3",
            ])

            # This is just an example of how you might want to format your data in a csv file.
            # Feel free to edit this to format it to your liking.

            writer.writeheader()
            for component in components:

                # This is an example of how to extract a specific parameter for each component.
                rohs_compliant_value = ""
                for parameter in component["details"]["parameters"]:
                    # Feel free to modify this to get the parameter you wish to.
                    # You will also need to modify the header, row and variable names accordingly
                    if parameter["name"] == "RoHS Compliant":
                        rohs_compliant_value = parameter["value"]

                row = {
                    "Item ID": component["name"],
                    "Name": component["comment"],
                    "Type": component["folder"]["name"],
                    "Description": component["description"],
                    "RoHS Compliant": rohs_compliant_value,
                }

                # In this example we are slicing the first 3 manufacturer parts
                # Feel free to not by removing the slice at the end
                # You will also need to add the appropriate column headers above
                for manufacturer_part in component["manufacturerParts"][:3]:
                    row.update({
                        "Manufacturer " + str(component["manufacturerParts"].index(manufacturer_part)+1):
                        manufacturer_part["companyName"]
                    })
                    row.update({
                        "Partnumber " + str(component["manufacturerParts"].index(manufacturer_part)+1):
                        manufacturer_part["partNumber"]
                    })

                writer.writerow(row)

    components = retrieve_components()

    csv_export(components)
    json_export(components)
