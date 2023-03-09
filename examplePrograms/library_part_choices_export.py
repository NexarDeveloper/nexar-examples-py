from nexarClients.design.nexarDesignClient import NexarClient
import os
import json

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
        manufacturerParts {
          supplierParts {
            companyName
            partNumber
            prices {
              currency
              price
            }
            stocks {
              locationName
              quantity
            }
          }
          octopartId
          companyName
          partNumber
          priority
        }
      }
    }
  }
}'''


if __name__ == "__main__":

    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]

    nexar = NexarClient(client_id, client_secret, ["design.domain", "openid", "user.access"])

    components = []

    def get_page(page_info):

        global components
        variables = {
            "workspaceURL": "Your workspace URL here",
            "after": page_info["endCursor"]
        }

        if page_info["hasNextPage"]:

            response = nexar.get_query(graphql_query, variables)
            components += response["desLibrary"]["components"]["nodes"]
            get_page(response["desLibrary"]["components"]["pageInfo"])

        else:

            with open("altium_library_components.json", "w") as library_components:

                json.dump(components, library_components)

    get_page({"hasNextPage": True, "endCursor": None})
