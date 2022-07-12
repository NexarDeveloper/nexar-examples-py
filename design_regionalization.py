from nexar_requests import NexarClient

LOCATION_QUERY = '''
query WorkspaceLocations {
    desWorkspaceLocations {
      name
      apiServiceUrl
    }
  }'''

WORKSPACES_QUERY = '''
query Workspaces {
    desWorkspaces {
      id
      name
      url
    }
  }'''

def get_available_regions(queryLocations, nexar):
    for index, location in enumerate(queryLocations):
        print(index + 1, ": ", location["name"])
    region = input("\n" + "Enter index to request to : ")
    region = int(region)
    if region <= 0 or region > len(queryLocations):
        print("\n" + "Invalid response, try again... " + "\n")
        get_available_regions(queryLocations, nexar)
    else: 
        queryLocation = queryLocations[region - 1]
        regionUrl = queryLocation["apiServiceUrl"]
        queryResult = nexar.get_query(WORKSPACES_QUERY, nexar_url=regionUrl)["desWorkspaces"]
        print(queryResult)

if __name__ == '__main__':
    token = input("Enter token : ")
    nexar = NexarClient(token)
    queryLocations = nexar.get_query(LOCATION_QUERY)["desWorkspaceLocations"]
    print("\n" + "Current available regions:" + "\n")
    get_available_regions(queryLocations, nexar)