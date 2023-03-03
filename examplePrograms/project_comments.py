import sys
import os
from nexarClients.design.nexarDesignClient import NexarClient
from nexarClients.design.design_helpers import (
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
                                createdAt
                                commentId
                                text
                                createdBy{
                                    userName
                                }
                                modifiedBy{
                                    userName
                                }
                                modifiedAt
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
    commentThreads = nexar.get_query(
        PROJECTWITHCOMMENTS_QUERY, variables
    )["desProjectById"]["design"]["workInProgress"]["variants"][0]["pcb"]["commentThreads"]
    return commentThreads


def list_comment_threads(commentThreads):
    print()

    if commentThreads == []:
        print("No comments available, exiting...")
        print()
        sys.exit()

    for thread in commentThreads:
        print("Comment thread :", thread["threadNumber"])
        print("Commend thread ID :", thread["commentThreadId"])

        for comment in thread["comments"]:
            print("Comment ID :", comment["commentId"])
            print("Created by :", comment["createdBy"]["userName"])
            print("Created at :", comment["createdAt"])
            print("Text :", comment["text"])

            if comment["createdAt"] != comment["modifiedAt"]:
                print("Modified by :", comment["modifiedBy"]["userName"])
                print("Modified at :", comment["modifiedAt"])

            print()


if __name__ == '__main__':

    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]
    nexar = NexarClient(client_id, client_secret, ["design.domain", "user.access", "openid"])

    workspaces = get_workspaces(nexar)
    workspace_id = get_workspace_id_from_user(workspaces)

    projects = get_projects(workspace_id, nexar)
    project_id = get_project_id_from_user(projects)

    commentThreads = get_comment_threads_from_project(project_id, nexar)
    list_comment_threads(commentThreads)
