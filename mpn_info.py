"""Example request for extracting GraphQL part data."""
import sys, argparse, json
from nexar_requests import NexarClient

QUERY_MPN = """
query ($mpn: String!) {
  supSearchMpn(q: $mpn) {
    results {
      part {
        category {
          parentId
          id
          name
          path
        }
        mpn
        manufacturer {
          name
        }
        shortDescription
        descriptions {
          text
          creditString
        }
        specs {
          attribute {
            name
            shortname
          }
          displayValue
        }
      }
    }
  }
}
"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Request part information based on a maunfacturer part number (MPN)."
    )
    parser.add_argument("mpn", help="The mpn for the part request.", type=str)
    parser.add_argument("-token", "-t", help="The Nexar access token.", type=str)
    args = parser.parse_args()
    nexar = NexarClient(args.token if (args.token is not None) else sys.stdin.readline().strip())

    variables = {
        "mpn": args.mpn
    }
    data = nexar.get_query(QUERY_MPN, variables)
    print(json.dumps(data["supSearchMpn"], indent = 1))
