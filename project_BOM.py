"""Example query for project BOM."""
import sys, argparse, json
from nexar_requests import NexarClient

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
    parser = argparse.ArgumentParser(
        description="Request BOM details for a project from the current version (WIP)."
    )
    parser.add_argument("projectId", help="The id for the project to query.", type=str)
    parser.add_argument("-token", "-t", help="The Nexar access token.", type=str)
    args = parser.parse_args()
    nexar = NexarClient(args.token if (args.token is not None) else sys.stdin.readline().strip())

    variables = {
        "projectId": args.projectId
    }
    data = nexar.get_query(QUERY, variables)
    print(json.dumps(data["desProjectById"]["design"]["workInProgress"]["variants"][0]["bom"]["bomItems"], indent = 1))
    