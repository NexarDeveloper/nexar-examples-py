import os, sys, json, time, requests, base64, argparse, csv
from nexar_requests import NexarClient
from typing import List

PROD_TOKEN_URL = "https://identity.nexar.com/connect/token"

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

def getParts():
    nexar = NexarClient(token)
    parser = argparse.ArgumentParser(
        description="Query multiple MPNs to produce a pricing table (output in .csv format)."
    )
    parser.add_argument("mpn", help="The mpn for the part request.", nargs="+", type=str)
    args = parser.parse_args()
    variables = {"queries": [{"mpn": mpn, "limit": 1, "start": 0} for mpn in args.mpn]}
    data = nexar.get_query(QUERY_MPN, variables)

    parts = []
    for match in data["supMultiMatch"]:
        for part in match["parts"]:
            offers = getSellerPricing(part, PRICEPOINTS)
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

def getLifecycleStatus(specs):
    if specs:
        lifecycleSpec = [i for (i) in specs if i.get('attribute',{}).get('shortname') == 'lifecyclestatus']
        if len(lifecycleSpec) > 0:
            return lifecycleSpec[0].get('value',{})
    return ''

def getSellerPricing(part, quantities) -> List:
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
    
def getToken():
    """Return the Nexar token from the client_id and client_secret provided."""
    client_id = os.environ['NEXAR_CLIENT_ID']
    client_secret = os.environ['NEXAR_CLIENT_SECRET']
    if not client_id or not client_secret:
        raise Exception("client_id and/or client_secret are empty")

    token = {}
    try:
        token = requests.post(
            url=PROD_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            },
            allow_redirects=False,
        ).json()

    except Exception:
        raise
    return token

def decodeJWT(token):
    return json.loads(
        (base64.urlsafe_b64decode(token.split(".")[1] + "==")).decode("utf-8")
    )
def doesFileExist(filePathAndName):
    return os.path.exists(filePathAndName)

def writeToJson():
    with open('tokenCache.json', "w") as f:                                     # opens json file
        newfile = {"Token" : token, "Expires" : decodeJWT(token)["exp"]}        # sets a variable with token and expiry time
        json.dump(newfile, f, indent=4)                                         # writes variable contents to json file with correct format

if __name__ == '__main__':

    if doesFileExist('tokenCache.json'):            # if the file exists
        with open('tokenCache.json')as f:           # assigns variables with the token and expiry time from the json file
            newfile = json.load(f)                  
            token = newfile["Token"]
            expiry_time = newfile["Expires"]
        current_time = time.time()

        if current_time > expiry_time:              # if the current time has passesd the expiry time (meaning the token has expired)
            token = getToken()["access_token"]     # gets new token
            writeToJson()                         # writes token and expiry time to json file

    else:                                           # if file doesn't exist, it creates new Json file and requests new token with expiry date, to be written to the json file
        token = getToken()["access_token"]         # gets new token
        writeToJson()                             # writes token and expiry time to json file
   
    getParts() 