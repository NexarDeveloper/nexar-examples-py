import sys
import os
from nexarClients.supply.nexarSupplyClient import NexarClient

LIMIT = 10
START = 0
ATTRIBUTE_NAME = "life_hours_"     # can be changed to any filter name that only pass integers
QUERY_CHOICE = ["Filter", "Sort"]
SORTING_ORDER = ["Ascending", "Descending"]

AVAILABLE_INPUTS_QUERY = '''
query Available_Input_Query($attributeNames: [String!]!) {
    supSearchMpn{
        specAggs(
            attributeNames: $attributeNames
            size: 10
        ) {
            buckets{
                floatValue
                displayValue
            }
        }
    }
}
'''

SUPPLY_QUERY = '''
query Supply_Query($limit: Int!, $filters: Map, $start: Int!, $sort: String, $sortDir: SupSortDirection) {
    supSearchMpn(
        limit: $limit
        filters: $filters
        start: $start
        sort: $sort
        sortDir: $sortDir
    ) {
        hits
        results{
            part{
                specs{
                    displayValue
                    value
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


def get_supsearchmpn_inputs_from_user():
    for index, item in enumerate(QUERY_CHOICE):
        print(index + 1, ":", item)

    print()
    supSearchMpnInput = input("Enter index to search for... : ")
    supSearchMpnInput = int(supSearchMpnInput)

    if supSearchMpnInput <= 0 or supSearchMpnInput > len(QUERY_CHOICE):
        print("\n" + "Invalid response, try again... " + "\n")
        return get_supsearchmpn_inputs_from_user()

    else:
        print()
        return QUERY_CHOICE[supSearchMpnInput - 1]


def get_sorting_decision_from_user():
    for index, item in enumerate(SORTING_ORDER):
        print(index + 1, ":", item)

    print()
    sortingDesicion = input("Enter index to search for... : ")
    sortingDesicion = int(sortingDesicion)

    if sortingDesicion <= 0 or sortingDesicion > len(SORTING_ORDER):
        print("\n" + "Invalid response, try again... " + "\n")
        return get_sorting_decision_from_user()

    else:
        if SORTING_ORDER[sortingDesicion - 1] == "Ascending":
            return "asc"

        else:
            return "desc"


def get_available_inputs(nexar, filter):
    variables = {
        "attributeNames": [filter]
    }

    availableInputs = nexar.get_query(AVAILABLE_INPUTS_QUERY, variables)["supSearchMpn"]["specAggs"][0]
    return availableInputs["buckets"]


def get_filter_value_from_user(availableInputs):
    inputsArray = []

    for floatValue in availableInputs:
        if floatValue["floatValue"] is not None:
            inputsArray.append(floatValue["floatValue"])
        else:
            inputsArray.append(floatValue["displayValue"])

    for index, item in enumerate(inputsArray):
        print(index + 1, ":", item)

    newIndex = index + 2
    print(newIndex, ": Enter own value")

    print()
    userDecision = input("Enter index to search for... : ")
    userDecision = int(userDecision)

    if userDecision <= 0 or userDecision > (len(inputsArray) + 1):
        print("\n" + "Invalid response, try again... " + "\n")
        return get_filter_value_from_user(availableInputs)

    else:
        if userDecision != newIndex:
            return inputsArray[userDecision - 1]
        else:
            print()
            userValue = input("Enter value to filter for... : ")
            return userValue


def supsearchmpn_query(nexar, limit, filters, start, sort, sortDir):
    variables = {
        "limit": limit,
        "filters": filters,
        "start": start,
        "sort": sort,
        "sortDir": sortDir
    }

    partInformation = nexar.get_query(SUPPLY_QUERY, variables)["supSearchMpn"]
    return partInformation


def do_query(filterOrSort):

    if filterOrSort == "Filter":

        availableInputs = get_available_inputs(nexar, ATTRIBUTE_NAME)
        userDecision = get_filter_value_from_user(availableInputs)

        filters = {
            ATTRIBUTE_NAME: userDecision
        }

        sort = None
        sortDir = None

        partInformation = supsearchmpn_query(nexar, LIMIT, filters, START, sort, sortDir)
        list_supsearchmpn_query(partInformation, list(filters))

    elif filterOrSort == "Sort":
        sort = ATTRIBUTE_NAME
        sortDir = get_sorting_decision_from_user()
        filters = None

        partInformation = supsearchmpn_query(nexar, LIMIT, filters, START, sort, sortDir)
        list_supsearchmpn_query(partInformation, [sort])


def list_supsearchmpn_query(partInformation, attributes):
    print()

    if partInformation == []:
        print("No parts available...")
        sys.exit()

    else:
        if partInformation["results"] is not None and partInformation["hits"] != 0:
            print("There are currently", partInformation["hits"], "parts available...")
            print()
            print("Printing first", LIMIT, "parts...")

            for part in partInformation["results"]:
                print()
                print("Part name :", part["part"]["name"])

                if part["part"]["category"] is not None:
                    print("Part category :", part["part"]["category"]["name"])
                else:
                    print("No part category available")

                print("Part manufacturer :", part["part"]["manufacturer"]["name"])
                print("Part MPN :", part["part"]["mpn"])
                print("Average number of parts available :", part["part"]["avgAvail"])

                if part["part"]["shortDescription"] != '':
                    print("Description :", part["part"]["shortDescription"])

                else:
                    print("No description available...")

                if part["part"]["medianPrice1000"] is not None:
                    print("Part median price :", part["part"]["medianPrice1000"]["price"])
                    print("Currency :", part["part"]["medianPrice1000"]["currency"])

                else:
                    print("No pricing available...")

                for displayValue in part["part"]["specs"]:

                    if displayValue["attribute"]["shortname"] in attributes:
                        print("Attribute name :", displayValue["attribute"]["name"])
                        print("Display value :", displayValue["displayValue"])

        else:
            print("No parts available... ")
    print()


if __name__ == '__main__':

    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]
    nexar = NexarClient(client_id, client_secret)
    print()

    filterOrSort = get_supsearchmpn_inputs_from_user()
    do_query(filterOrSort)
