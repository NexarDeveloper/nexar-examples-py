"""Example query for workspace info."""
import sys, argparse, json
from nexar_requests import NexarClient

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
    parser = argparse.ArgumentParser(
        description="Query a workspace for project information."
    )
    parser.add_argument("name", help="The name for the workspace to query.", type=str)
    parser.add_argument("-token", "-t", help="The Nexar access token.", type=str)
    args = parser.parse_args()
    nexar = NexarClient(args.token if (args.token is not None) else sys.stdin.readline().strip())

    variables = {
        "workspace": args.name
    }
    data = nexar.get_query(QUERY, variables)
    print(json.dumps(data["desWorkspaces"], indent = 1))
    