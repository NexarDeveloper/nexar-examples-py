from nexar_requests import NexarClient

WORKSPACES_QUERY = '''
query Workspaces{
    desWorkspaces{
        id
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
        }
    }
}
'''

PROJECTWITHCOMMENTS_QUERY = '''
query desProjectById($projectId : ID!) {
    desProjectById(
    id: $projectId
    ) {
        design{
            workInProgress{
                variants{
                    pcb{
                        commentThreads{
                            threadNumber
                            comments{
                                text
                                createdBy{
                                    userName
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

def get_projects(nexar):
    workspaces = nexar.get_query(WORKSPACES_QUERY)["desWorkspaces"]
    variables = {
        "workspaceId": workspaces[0]["id"]
    }
    projects = nexar.get_query(WORKSPACEBYID_QUERY, variables)["desWorkspaceById"]["projects"]
    return projects

def get_project_id_from_user(projects):
    print()
    for index, project in enumerate(projects):
        print(index + 1, ": ", project["name"])
    option = input("\n" + "Enter number for project to visit... : ")
    option = int(option)
    if option <= 0 or option > len(projects):
        print("\n" + "Invalid response, try again... " + "\n")
        get_project_id_from_user(projects)
    else:
        return projects[option-1]["id"]

def list_comment_threads_for_project(projects, nexar):
        variables = {
        "projectId": projects
        }
        commentThreads = nexar.get_query(PROJECTWITHCOMMENTS_QUERY, variables)["desProjectById"]["design"]["workInProgress"]["variants"][0]["pcb"]["commentThreads"]
        print()
        if commentThreads == []:
            print("No comments available")
            print()
        for thread in commentThreads:
            print("Comment thread", thread["threadNumber"], ":")
            for comment in thread["comments"]:
                print("Created by :", comment["createdBy"]["userName"])
                print(comment["text"])
                print()

if __name__ == '__main__':
    token = input("Enter token : ")
    nexar = NexarClient(token)
    projects = get_projects(nexar)
    project_id = get_project_id_from_user(projects)
    list_comment_threads_for_project(project_id, nexar)