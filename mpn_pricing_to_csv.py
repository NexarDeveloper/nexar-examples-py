"""Example request for extracting GraphQL part data."""
import sys, argparse, json
import csv
from typing import List
from nexar_requests import NexarClient

QUERY_MPN = """
query ($queries: [SupPartMatchQuery!]!) {
  supMultiMatch (queries: $queries) {
    hits
    parts {
      mpn
      name
      id
      sellers {
        country
        company {
          name
          homepageUrl
        }
        offers {
          clickUrl
          inventoryLevel
          moq
          packaging
          sku
          updated
          prices {
            currency
            price
            quantity
          }
        }
      }
    }  
  }
}
"""
PRICEPOINTS = [1,10,25,50,100,250,500,1000,2500,5000,10000,25000,50000]


def get_seller_pricing(part, quantities) -> List:
    offers = []
    for seller in part["sellers"]:
        for offer in seller["offers"]:
            if (not len(offer["prices"])): continue

            prices = sorted(offer.pop("prices"), key=lambda o: o["quantity"])
            nextPrice = prices.pop(0)
            for q in quantities:
                while (len(prices) and prices[0]["quantity"]< q): nextPrice = prices.pop(0)
                offer[q] = nextPrice["price"]

        # add info to the first offer from this seller
        seller["offers"][0].update({
            "companyName":  seller["company"]["name"],
            "homepageUrl":  seller["company"]["homepageUrl"],
            "country":      seller["country"]
        })
        offers = offers + (seller["offers"])

    # add info to the first offer for this part
    offers[0].update({
        "mpn":  part["mpn"],
        "name": part["name"],
        "id":   part["id"]
    })
    return offers

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
      description="Query multiple MPNs to produce a pricing table (output in .csv format)."
    )
    parser.add_argument("mpn", help="The mpn for the part request.", nargs="+", type=str)
    parser.add_argument("-token", "-t", help="The Nexar access token.", type=str)
    args = parser.parse_args()
    nexar = NexarClient(args.token if (args.token is not None) else sys.stdin.readline().strip())

    variables = {"queries": [{"mpn": mpn, "limit": 1, "start": 0} for mpn in args.mpn]}
    data = nexar.get_query(QUERY_MPN, variables)

    parts = []
    for match in data["supMultiMatch"]:
        for part in match["parts"]:
            offers = get_seller_pricing(part, PRICEPOINTS)
            parts = parts + offers

    writer = csv.DictWriter(sys.stdout, fieldnames = [
      "mpn",
      "name",
      "id",
      "country",
      "companyName",
      "homepageUrl",
      "clickUrl",
      "inventoryLevel",
      "moq",
      "packaging",
      "sku",
      "updated"] + 
      PRICEPOINTS, extrasaction='ignore')
        
    writer.writeheader() 
    writer.writerows(parts) 