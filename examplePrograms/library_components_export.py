from nexarClients.design.nexarDesignClient import NexarClient
import os
import json
import csv

# This is the API query, feel free to chop and change this to suit your use case.
# We recommend building queries in an IDE such as BananaCakePop or Postman.
# You can use BananaCakePop in a browser here: https://api.nexar.com/graphql/

workspaceURL = "Your workspace URL here"

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

        while page_info["hasNextPage"] is True:

            variables = {
                "workspaceURL": workspaceURL,
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

            writer = csv.writer(csv_file)

            # This is just an example of how you might want to format your data in a csv file.
            # Feel free to edit this to format it to your liking.

            writer.writerow([
                # These are the headers for the file
                "Item ID", "Name", "Type", "Description",
                "RoHS Compliant",
                "Manufacturer 1", "Partnumber 1",
                "Manufacturer 2", "Partnumber 2",
                "Manufacturer 3", "Partnumber 3"
            ])
            writer.writerow([])

            for component in components:

                # This is an example of how to extract a specific parameter for each component.
                # Feel free to modify this to get the parameter you wish to.

                rohs_compliant_value = ""
                for parameter in component["details"]["parameters"]:
                    if parameter["name"] == "RoHS Compliant":
                        rohs_compliant_value = parameter["value"]

                row = [
                    component["name"],
                    component["comment"],
                    component["folder"]["name"],
                    component["description"],
                    rohs_compliant_value,
                ]

                for manufacturerPart in component["manufacturerParts"]:
                    row.append(manufacturerPart["companyName"])
                    row.append(manufacturerPart["partNumber"])

                writer.writerow(row)

    components = retrieve_components()

    csv_export(components)
    json_export(components)
