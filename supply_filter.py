from nexar_requests import NexarClient
import sys

LIMIT = 10
START = 0
FILTER_NAME = "life_hours_"     # can be changed to any filter name

AVAILABLE_INPUTS_QUERY = '''
query Available_Input_Query($attributeNames: [String!]!) {
    supSearchMpn{
        specAggs(
            attributeNames: $attributeNames
        ) {
            buckets{
                floatValue
            }
        }
    }
}
'''

SUPPLY_QUERY = '''
query Supply_Query($limit: Int!, $filters: Map!, $start: Int!) {
    supSearchMpn(
        limit: $limit
        filters: $filters
        start: $start
    ) {
        hits
        results{
            part{
                specs{
                    displayValue
                    attribute{
                        name
                        shortname
                    }
                }
                name
                category{
                    name
                }
                manufacturer{
                    name
                }
                mpn
                shortDescription
                avgAvail
                medianPrice1000{
                    price
                    currency
                }
            }
        }
    }
}
'''
def get_available_inputs(nexar, filter):

    variables = {
        "attributeNames": [filter]
    }

    availableInputs = nexar.get_query(AVAILABLE_INPUTS_QUERY, variables)["supSearchMpn"]["specAggs"][0]
    return availableInputs

def get_user_decision(availableInputs):
    inputsArray = []

    for floatValue in availableInputs["buckets"]:
        inputsArray.append(floatValue["floatValue"])
    
    for index, item in enumerate(inputsArray):
        print(index + 1, ":", item)

    print()
    userDecision = input("Enter index to search for... : ")
    userDecision = int(userDecision)

    if userDecision <=0 or userDecision > len(inputsArray):
        print("\n" + "Invalid response, try again... " + "\n")
        return get_user_decision(availableInputs)
    else:
        return inputsArray[userDecision - 1]
        

def supsearchmpn_query(nexar, limit, filters, start):
    variables = {
        "limit": limit,
        "filters": filters,
        "start": start
    }

    partInformation = nexar.get_query(SUPPLY_QUERY, variables)["supSearchMpn"]
    return partInformation

def list_supsearchmpn_query(partInformation, filters):
    print()
    
    if partInformation == []:
        print("No parts available...")
        sys.exit()
    
    else:
        if partInformation["results"] != None and partInformation["hits"] != 0:
            print("There are currently", partInformation["hits"], "parts available...")
            print()
            print("Printing first", LIMIT, "parts...")
            
            for part in partInformation["results"]:
                print()
                print("Part name :", part["part"]["name"])
                
                if part["part"]["category"] != None:
                    print("Part category :", part["part"]["category"]["name"])
                else:
                    print("No part category available")

                print("Part manufacturer :", part["part"]["manufacturer"]["name"])
                print("Part MPN :", part["part"]["mpn"])
                print("Average number of parts available :", part["part"]["avgAvail"])
                print("Description :", part["part"]["shortDescription"])
                
                if part["part"]["medianPrice1000"] != None:
                    print("Part median price :", part["part"]["medianPrice1000"]["price"])
                    print("Currency :", part["part"]["medianPrice1000"]["currency"])
            
                else:
                    print("No pricing available...")

                for displayValue in part["part"]["specs"]:
                
                    if displayValue["attribute"]["shortname"] in filters:
                        print("Attribute name :", displayValue["attribute"]["name"])
                        print("Display value :", displayValue["displayValue"])    

        else:
            print("No parts available... ")
    print()

if __name__ == '__main__':
    token = input("Enter token : ")
    nexar = NexarClient(token)
    print()

    availableInputs = get_available_inputs(nexar, FILTER_NAME)
    userDecision = get_user_decision(availableInputs)

    filters = {
        FILTER_NAME: userDecision
    }

    partInformation = supsearchmpn_query(nexar, LIMIT, filters, START)
    list_supsearchmpn_query(partInformation, list(filters))