"""Sample project query."""
import sys, argparse, json
from nexar_requests import NexarClient

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
    parser = argparse.ArgumentParser(
      description="Query designItems for a project from the current version (WIP)."
    )
    parser.add_argument("projectId", help="The id for the project to query.", type=str)
    parser.add_argument("-token", "-t", help="The Nexar access token.", type=str)
    args = parser.parse_args()
    nexar = NexarClient(args.token if (args.token is not None) else sys.stdin.readline().strip())

    variables = {
        "projectId": args.projectId
    }
    for response in nexar.NodeIter(QUERY, variables, lambda x: x["desProjectById"]["design"]["workInProgress"]["variants"][0]["pcb"]["designItems"]):
        print(json.dumps(response, indent = 1))
