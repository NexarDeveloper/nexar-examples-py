"""Sample project query."""
import os
import json
from nexarClients.design.nexarDesignClient import NexarClient

QUERY = """
query DesignInfo($projectId: ID!, $cursor: String) {
  desProjectById(
    id: $projectId
    ){
    name
    design {
      workInProgress {
        variants {
          name
          pcb {
            designItems(after: $cursor) {
              totalCount
              pageInfo {
                endCursor
                hasNextPage
              }
              nodes {
                designator
                description
                layer {
                  name
                }
                position {
                  xMils
                  yMils
                }
                pads {
                  designator
                  net {
                    name
                  }
                }
                component {
                  name
                  manufacturerParts {
                    partNumber
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""


if __name__ == '__main__':

    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]
    nexar = NexarClient(client_id, client_secret, ["design.domain", "user.access", "openid"])

    projectId = input("Enter project ID: ")
    variables = {
        "projectId": projectId
    }
    for response in nexar.NodeIter(
        QUERY,
        variables,
        lambda x: x["desProjectById"]["design"]["workInProgress"]["variants"][0]["pcb"]["designItems"]
    ):
        print(json.dumps(response, indent=1))
