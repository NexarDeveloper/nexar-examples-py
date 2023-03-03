"""Example query for project BOM."""
import sys
import os
import json
from nexarClients.design.nexarDesignClient import NexarClient

QUERY = """
query ProjectBOM($projectId: ID!) {
  desProjectById (
    id: $projectId
    ) {
    name
    design {
      workInProgress {
        variants {
          name
          bom {
            bomItems {
              component {
                name
                description
                manufacturerParts {
                  partNumber
                }
              }
              bomItemInstances {
                designator
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
    nexar = NexarClient(client_id, client_secret, ["design.domain", "user.access"])

    projectId = input("Enter project ID: ")
    if not projectId:
        sys.exit

    variables = {
        "projectId": projectId
    }
    data = nexar.get_query(QUERY, variables)
    print(json.dumps(data["desProjectById"]["design"]["workInProgress"]["variants"][0]["bom"]["bomItems"], indent=1))
