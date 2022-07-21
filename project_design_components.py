from nexar_requests import NexarClient
import sys

WORKSPACES_QUERY = '''
query Workspaces {
    desWorkspaces{
        id
        name
    }
}
'''
WORKSPACEBYID_QUERY = '''
query WorkspaceById($workspaceId: ID!) {
    desWorkspaceById(
    id: $workspaceId
    ) {
        projects{
            id
            name
            description
        }
    }
}
'''
GETCOMPONENTINFOFORPROJECT_QUERY = '''
query GetComponentInfoForProject($projectId: ID!, $queryAmount: Int!) {
    desProjectById(
        id: $projectId
    ) {
        id
        description
        name
        design{
            workInProgress{
                variants{
                    name
                    pcb{
                        designItems(
                            first: $queryAmount
                        ) {
                            totalCount
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
                        }
                    }
                }
            }
        }
    }
}
'''
def get_workspaces(nexar):
    workspaces = nexar.get_query(WORKSPACES_QUERY)["desWorkspaces"]
    return workspaces

def get_workspace_id_from_user(workspaces):
    print("\n" + "List of available workspaces to visit..." + "\n")
    for index, workspace in enumerate(workspaces):
        print(index + 1, ":", workspace["name"] + "\n")
    chosenWorkspace = input("Enter number for workspace to visit... : ")
    chosenWorkspace = int(chosenWorkspace)
    if chosenWorkspace <= 0 or chosenWorkspace > len(workspaces):
        print("\n" + "Invalid response, try again... ")
        get_workspace_id_from_user(workspaces)
    else:
        return workspaces[chosenWorkspace-1]["id"]

def get_projects(workspace_id, nexar):
    variables = {
        "workspaceId": workspace_id
    }
    projects = nexar.get_query(WORKSPACEBYID_QUERY, variables)["desWorkspaceById"]["projects"]
    return projects

def get_project_id_from_user(projects):
    print("\n" + "List of available projects to visit..." + "\n")
    for index, project in enumerate(projects):
        print(index + 1, ":", project["name"])
        if project["description"] != "":
            print("Description :", project["description"])
        else:
            print("No description available...")
        print()
    chosenProject = input("Enter number for project to visit... : ")
    chosenProject = int(chosenProject)
    if chosenProject <= 0 or chosenProject > len(projects):
        print("\n" + "Invalid response, try again... ")
        get_project_id_from_user(projects)
    else:
        return projects[chosenProject-1]["id"]

def get_component_info_for_project(project_id, nexar):
    queryAmount = 25
    variables = {
        "projectId": project_id,
        "queryAmount": queryAmount
    }
    componentInfoForProject = nexar.get_query(GETCOMPONENTINFOFORPROJECT_QUERY, variables)["desProjectById"]["design"]["workInProgress"]["variants"]
    return componentInfoForProject

def list_component_info_for_project(componentInfo):
    print()
    print("All components in project :")
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

if __name__ == '__main__':
    token = input("Enter token : ")
    nexar = NexarClient(token)
    workspaces = get_workspaces(nexar)
    workspace_id = get_workspace_id_from_user(workspaces)
    projects = get_projects(workspace_id, nexar)
    project_id = get_project_id_from_user(projects)
    componentInfo = get_component_info_for_project(project_id, nexar)
    list_component_info_for_project(componentInfo)