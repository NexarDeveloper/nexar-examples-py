from nexar_requests import NexarClient
import sys, math

NEXT_PAGE = "Next page"
PREVIOUS_PAGE = "Previous page"
CHOOSE_PAGE = "Choose Page"
EXIT = "Exit"

PAGE_OPTIONS = [NEXT_PAGE, PREVIOUS_PAGE, CHOOSE_PAGE, EXIT]

LIMIT = 10
IN_STOCK_ONLY = True        # can be changed depending on what the user wants to query


SUPPLY_QUERY = '''
query Supply_Query($limit: Int!, $inStockOnly: Boolean!, $part: String, $start: Int!) {
    supSearchMpn(
        limit: $limit
        inStockOnly: $inStockOnly
        q: $part
        start: $start
    ) {
        hits
        results{
            part{
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

def supsearch_query(nexar, limit, inStockOnly, part, start):
    variables = {
        "limit": limit,
        "inStockOnly": inStockOnly,
        "part": part,
        "start": start
    }

    partInformation = nexar.get_query(SUPPLY_QUERY, variables)["supSearchMpn"]
    return partInformation

def list_supsearch_query(partInformation, page, numberOfPages):
    print()
    
    if partInformation == []:
        print("No parts available...")
        sys.exit()
    
    else:
        print("Page", page, "of", numberOfPages)
        
        if partInformation["results"] != None and partInformation["hits"] != 0:
            print("There are currently", partInformation["hits"], "parts available...")
            
            for part in partInformation["results"]:
                
                if part != []:
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

        else:
            print("No parts that have that name are available... ")
    print()

def get_page_decision_from_user():
    for index, item in enumerate(PAGE_OPTIONS):
        print(index + 1, ":", item)

    print()
    userPageDecision = input("Enter number for page to visit... : ")
    userPageDecision = int(userPageDecision)
    print()

    if userPageDecision <= 0 or userPageDecision > len(PAGE_OPTIONS):
        print("\n" + "Invalid response, try again... ")
        get_page_decision_from_user()
    
    else:
        return PAGE_OPTIONS[userPageDecision - 1]

def move_page(userDecision, numberOfPages, limit, inStockOnly, part, start, page):
    if userDecision == EXIT:
        print("Exiting system...")
        sys.exit()
    
    elif userDecision == NEXT_PAGE:
        
        if page != numberOfPages:

            page = page + 1
            start = start + limit
            
            partInformation = supsearch_query(nexar, limit, inStockOnly, part, start)
            list_supsearch_query(partInformation, page, numberOfPages)

        else:
            print("\n" + "No next page available, try again...")
        
        return page, start
    
    elif userDecision == PREVIOUS_PAGE:

        if page != 1:

            page = page - 1
            start = start - limit

            partInformation = supsearch_query(nexar, limit, inStockOnly, part, start)
            list_supsearch_query(partInformation, page, numberOfPages)

        else:
            print("\n" + "No previous page available, try again...")
            
        return page, start
   
    elif userDecision == CHOOSE_PAGE:
        chosenPage = input("Enter page number... : ")
        chosenPage = int(chosenPage)
        
        if chosenPage <= 0 or chosenPage > numberOfPages:
            
            print()
            print("Invalid page number...")
            print()
        
        else:
            page = chosenPage
            start = (chosenPage * limit) - limit

            partInformation = supsearch_query(nexar, limit, inStockOnly, part, start)
            list_supsearch_query(partInformation, page, numberOfPages)

        return page, start

if __name__ == '__main__':
    token = input("Enter token : ")
    nexar = NexarClient(token)
    
    print()
    part = input("Enter part MPN... : ")
    start = 0
    page = 1

    partInformation = supsearch_query(nexar, LIMIT, IN_STOCK_ONLY, part, start)
    hits = partInformation["hits"]
    numberOfPages = math.ceil(hits / LIMIT)
    list_supsearch_query(partInformation, page, numberOfPages)

    while True:
        userDecision = get_page_decision_from_user()
        page, start = move_page(userDecision, numberOfPages, LIMIT, IN_STOCK_ONLY, part, start, page)