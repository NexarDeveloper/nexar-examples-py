"""Example request for extracting GraphQL part data."""
import sys
import os
import json
from nexarClients.supply.nexarSupplyClient import NexarClient

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

    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]
    nexar = NexarClient(client_id, client_secret)

    mpn = input("Enter a MPN: ")
    if not mpn:
        sys.exit()

    variables = {
        "mpn": mpn
    }
    data = nexar.get_query(QUERY_MPN, variables)
    print(json.dumps(data["supSearchMpn"], indent=1))
