from nexar_requests import NexarClient
import sys
from design_helpers import (
    get_workspaces,
    get_workspace_id_from_user,
    get_projects,
    get_project_id_from_user
)

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
                            commentThreadId
                            modifiedBy{
                                userName
                            }
                            comments{
                                commentId
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

def get_comment_threads_from_project(project_id, nexar):
    variables = {
        "projectId": project_id
    }
    commentThreads = nexar.get_query(PROJECTWITHCOMMENTS_QUERY, variables)["desProjectById"]["design"]["workInProgress"]["variants"][0]["pcb"]["commentThreads"]
    return commentThreads

def list_comment_threads(commentThreads):
    print()
   
    if commentThreads == []:
        print("No comments available, exiting...")
        print()
        sys.exit()
    
    for thread in commentThreads:
        print("Comment thread :", thread["threadNumber"])
        print("Commend thread ID : ", thread["commentThreadId"])
        
        for comment in thread["comments"]:
            print("Comment ID :", comment["commentId"])
            print("Created by :", comment["createdBy"]["userName"])
            print("Text :", comment["text"])
            print()

if __name__ == '__main__':
    token = input("Enter token : ")
    nexar = NexarClient(token)

    workspaces = get_workspaces(nexar)
    workspace_id = get_workspace_id_from_user(workspaces)

    projects = get_projects(workspace_id, nexar)
    project_id = get_project_id_from_user(projects)

    commentThreads = get_comment_threads_from_project(project_id, nexar)
    list_comment_threads(commentThreads)