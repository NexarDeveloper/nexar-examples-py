from nexar_requests import NexarClient
import sys
from design_helpers import (
    get_workspaces,
    get_workspace_id_from_user,
    get_projects,
    get_project_id_from_user
)

COMPONENT_COUNT = 4

NEXT_PAGE = "Next page"
PREVIOUS_PAGE = "Previous page"
EXIT = "Exit"

PAGE_OPTIONS = [NEXT_PAGE, PREVIOUS_PAGE, EXIT]

GETCOMPONENTINFOFORPROJECT_QUERY = '''
query GetComponentInfoForProject($projectId: ID!, $first: Int, $after: String, $last: Int, $before: String) {
    desProjectById(
        id: $projectId
    ) {
        design{
            workInProgress{
                variants{
                    name
                    pcb{
                        designItems(
                            first: $first
                            after: $after
                            last: $last
                            before: $before
                        ) {
                            nodes{
                                designator
                                component{
                                    name
                                    comment
                                    description
                                    details{
                                        parameters{
                                            name
                                            value
                                        }
                                    }
                                }
                            }
                            pageInfo{
                                hasNextPage
                                hasPreviousPage
                                startCursor
                                endCursor
                            }
                        }
                    }
                }
            }
        }
    }
}
'''
def get_component_info_for_project(project_id, nexar, cursor, forwards):
    first = COMPONENT_COUNT if forwards else None
    last = None if forwards else COMPONENT_COUNT
    startCursor = cursor if forwards else None
    endCursor = None if forwards else cursor
    variables = {
        "projectId": project_id,
        "first": first,
        "after": startCursor,
        "last": last,
        "before": endCursor
    }

    componentInfoForProject = nexar.get_query(GETCOMPONENTINFOFORPROJECT_QUERY, variables)["desProjectById"]["design"]["workInProgress"]["variants"]
    
    newStartCursor = componentInfoForProject[0]["pcb"]["designItems"]["pageInfo"]["endCursor"]
    newEndCursor = componentInfoForProject[0]["pcb"]["designItems"]["pageInfo"]["startCursor"]
    
    return componentInfoForProject, newStartCursor, newEndCursor

def list_component_info_for_project(componentInfo, page):
    print()
    print("List of components in project, on page :", page)

    if componentInfo == []:
        print("No component information available...")
        print()
        sys.exit()

    else:
        print("Name of variant :", componentInfo[0]["name"])
        for designItem in componentInfo[0]["pcb"]["designItems"]["nodes"]:
            print("Designator :", designItem["designator"])

            if designItem["component"] != None:
                print("Name :", designItem["component"]["name"])

                if designItem["component"]["comment"] != "":
                    print("Comment :", designItem["component"]["comment"])
                else:
                    print("No comment available...")

                if designItem["component"]["comment"] != "":
                    print("Description :", designItem["component"]["description"])
                else:
                    print("No desciption available...")

                if designItem["component"]["details"]["parameters"] != []:

                    for index in designItem["component"]["details"]["parameters"]:
                        print()
                        print("Parameter name :", index["name"])

                        if index["value"] != "":
                            print("Parameter value :", index["value"])
                        else:
                            print("No parameter value available...")
            else:
                print("No component information is available...")
            print()
  
        print("Has next page :", componentInfo[0]["pcb"]["designItems"]["pageInfo"]["hasNextPage"])
        print("Has previous page :", componentInfo[0]["pcb"]["designItems"]["pageInfo"]["hasPreviousPage"])

def get_page_decision_from_user():
    print()
    for index, item in enumerate(PAGE_OPTIONS):
        print(index + 1, ":", item)

    print()
    userPageDecision = input("Enter number for page to visit... : ")
    userPageDecision = int(userPageDecision)

    if userPageDecision <= 0 or userPageDecision > len(PAGE_OPTIONS):
        print("\n" + "Invalid response, try again... ")
        get_page_decision_from_user()
    else:
        return PAGE_OPTIONS[userPageDecision - 1]

def move_page(pageInfo, userPageDecision, project_id, nexar, startCursor, endCursor, page): 
           
    if userPageDecision == EXIT:
        print("\n" + "Exiting system...")
        sys.exit()

    elif userPageDecision == NEXT_PAGE:

        if pageInfo["hasNextPage"] == True:
            
            page = page + 1

            componentInfo, startCursor, endCursor = get_component_info_for_project(project_id, nexar, startCursor, True)
            pageInfo = componentInfo[0]["pcb"]["designItems"]["pageInfo"]
            list_component_info_for_project(componentInfo, page)
            
        else:
            print("\n" + "No next page available, try again...")

        return  startCursor, endCursor, pageInfo

    elif userPageDecision == PREVIOUS_PAGE:

        if pageInfo["hasPreviousPage"] == True:

            page = page - 1

            componentInfo, startCursor, endCursor = get_component_info_for_project(project_id, nexar, endCursor, False)
            pageInfo = componentInfo[0]["pcb"]["designItems"]["pageInfo"]
            list_component_info_for_project(componentInfo, page)

        else:
            print("\n" + "No previous page available, try again...")

        return startCursor, endCursor, pageInfo


if __name__ == '__main__':
    token = input("Enter token : ")
    nexar = NexarClient(token)

    workspaces = get_workspaces(nexar)
    workspace_id = get_workspace_id_from_user(workspaces)

    projects = get_projects(workspace_id, nexar)
    project_id = get_project_id_from_user(projects)

    page = 1

    componentInfo, startCursor, endCursor = get_component_info_for_project(project_id, nexar, None, True)
    list_component_info_for_project(componentInfo, page)
    pageInfo = componentInfo[0]["pcb"]["designItems"]["pageInfo"]

    while True:
        userPageDecision = get_page_decision_from_user()
        startCursor, endCursor, pageInfo = move_page(pageInfo, userPageDecision, project_id, nexar, startCursor, endCursor, page) 