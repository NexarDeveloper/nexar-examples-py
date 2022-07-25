from nexar_requests import NexarClient

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


def get_workspaces(nexar: NexarClient):
    workspaces = nexar.get_query(WORKSPACES_QUERY)["desWorkspaces"]
    return workspaces

def get_workspace_id_from_user(workspaces: list):
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

def get_projects(workspace_id: str, nexar: NexarClient):
    variables = {
        "workspaceId": workspace_id
    }
    projects = nexar.get_query(WORKSPACEBYID_QUERY, variables)["desWorkspaceById"]["projects"]
    return projects

def get_project_id_from_user(projects: list):
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