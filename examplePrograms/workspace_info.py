"""Example query for workspace info."""
import os
import json
from nexarClients.design.nexarDesignClient import NexarClient

QUERY = """
query Workspace($workspace: String!) {
  desWorkspaces(where: {name: {eq: $workspace}}) {
    url
    name
    description
    projects {
      id
      name
      description
    }
  }
}
"""


if __name__ == '__main__':

    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]
    nexar = NexarClient(client_id, client_secret, ["design.domain", "user.access", "openid"])

    workspaceName = input("Enter workspace name: ")
    variables = {
        "workspace": workspaceName
    }
    data = nexar.get_query(QUERY, variables)
    print(json.dumps(data["desWorkspaces"], indent=1))
