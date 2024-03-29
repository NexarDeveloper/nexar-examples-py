import sys
import os
from nexarClients.design.nexarDesignClient import NexarClient
from nexarClients.design.design_helpers import (
    get_workspaces,
    get_workspace_id_from_user,
    get_projects,
    get_project_id_from_user
)

UPDATE_ACTION = "Update comment"
CREATE_ACTION = "Create comment"
DELETE_ACTION = "Delete comment"
CREATE_THREAD_ACTION = "Create comment thread"
DELETE_THREAD_ACTION = "Delete comment thread"

COMMENT_ACTIONS = [UPDATE_ACTION, CREATE_ACTION, DELETE_ACTION, CREATE_THREAD_ACTION, DELETE_THREAD_ACTION]

PROJECTWITHCOMMENTS_QUERY = '''
query desProjectById($projectId : ID!) {
    desProjectById(
    id: $projectId
    ) {
        design{
            workInProgress{
                variants{
                    pcb{
                        documentId
                        documentName
                        commentThreads{
                            threadNumber
                            commentThreadId
                            comments{
                                commentId
                                text
                                createdBy{
                                    userName
                                }
                                modifiedBy{
                                    userName
                                }
                                modifiedAt
                                createdAt
                            }
                        }
                    }
                }
            }
        }
    }
}
'''
UPDATECOMMENT_MUTATION = '''
mutation desUpdateComment($commentId : String!, $commentThreadId : String!, $entityId : ID!, $text : String!) {
    desUpdateComment(input: {
        entityId: $entityId,
        commentThreadId: $commentThreadId,
        commentId: $commentId,
        text: $text
    }) {
        errors {
            message
        }
    }
}
'''
CREATECOMMENT_MUTATION = '''
mutation desCreateComment($entityId : ID!, $commentThreadId : String!, $text : String!) {
    desCreateComment(input: {
        entityId: $entityId,
        commentThreadId : $commentThreadId,
        text: $text
    }) {
        errors {
            message
        }
    }
}
'''
DELETECOMMENT_MUTATION = '''
mutation desDeleteComment($entityId : ID!, $commentThreadId : String!, $commentId : String!) {
    desDeleteComment(input: {
        entityId: $entityId,
        commentThreadId: $commentThreadId,
        commentId: $commentId
    }) {
        errors {
            message
        }
    }
}
'''

CREATECOMMENTTHREAD_MUTATION = '''
mutation createCommentThread ($entityId: ID!, $documentId: String!, $text: String!){
    desCreateCommentThread (input: {
        documentType: PCB,
        commentContextType: NONE,
        entityId: $entityId,
        documentId: $documentId,
        text: $text,
    }) {
        commentThreadId
        commentId
        errors {
            message
        }
    }
}
'''

DELETECOMMENTTHREAD_MUTATION = '''
mutation deleteCommentThread ($entityId: ID!, $commentThreadId: String!) {
    desDeleteCommentThread (input: {
        entityId: $entityId,
        commentThreadId: $commentThreadId
    }) {
        errors {
            message
        }
    }
}
'''


def get_pcb_from_project(project_id, nexar):
    variables = {
        "projectId": project_id
    }
    pcb = nexar.get_query(
        PROJECTWITHCOMMENTS_QUERY, variables
    )["desProjectById"]["design"]["workInProgress"]["variants"][0]["pcb"]
    return pcb


def list_comment_threads(pcb):
    commentThreads = pcb["commentThreads"]
    print()

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


def get_user_decision(pcb):
    if pcb["commentThreads"] == []:                                    # if there are no comments
        print("No comment to update, or thread to add to...")

        while True:
            new_thread_decision = input("Would you like to create a comment thread? (Y/N): ")

            if new_thread_decision.lower() == "n":
                sys.exit()
            elif new_thread_decision.lower() == "y":
                return CREATE_THREAD_ACTION
            else:
                print("Invalid response.\n")
                continue

    for index, item in enumerate(COMMENT_ACTIONS):
        print(index + 1, ":", item)

    while True:

        print()
        choice = input("Enter number to update, create, delete a comment or create a new comment thread: ")
        choice = int(choice)
        print()

        if choice <= 0 or choice > len(COMMENT_ACTIONS):
            print("Invalid response, try again... " + "\n")
            continue

        return COMMENT_ACTIONS[choice-1]


def change_comment(pcb, choice, entityId):
    if choice == CREATE_ACTION:
        commentThreadId = input("Enter comment thread ID for the section you want to add a comment to... : ")
        create_comment(nexar, entityId, commentThreadId)

    elif choice == CREATE_THREAD_ACTION:
        create_comment_thread(nexar, entityId, pcb["documentId"])

    elif choice == DELETE_THREAD_ACTION:
        while True:

            commentThreadId = input("Enter a comment thread ID for the thread you want to delete... : ")
            valid_comment_thread_ids = []

            for commentThread in pcb["commentThreads"]:
                valid_comment_thread_ids.append(commentThread["commentThreadId"])

            if commentThreadId in valid_comment_thread_ids:
                break
            else:
                continue

        delete_comment_thread(nexar, entityId, commentThreadId)

    else:
        if choice == UPDATE_ACTION:
            currentText = "Enter comment ID for the comment you want to change... : "

        elif choice == DELETE_ACTION:
            currentText = "Enter comment ID for the comment you want to delete... : "

        commentId = input(currentText)
        commentThreadId = ""

        for commentThread in pcb["commentThreads"]:

            for comments in commentThread["comments"]:
                # gets commentThreadId from commentId

                if comments["commentId"] == commentId:
                    commentThreadId = commentThread["commentThreadId"]

        # if the for loop could not find a commentThreadId, meaning the comment ID used was invalid
        if commentThreadId == "":
            print("\n" + "Invalid Comment ID..." + "\n")
            change_comment(pcb, choice, entityId)
            # loops until correct comment ID is used

        if choice == UPDATE_ACTION:
            update_comment(nexar, entityId, commentThreadId, commentId)

        else:
            delete_comment(nexar, entityId, commentThreadId, commentId)


def create_comment_thread(nexar, entityId, documentId):
    print()
    text = input("Enter comment: ")
    variables = {
        "entityId": entityId,
        "documentId": documentId,
        "text": text,
    }

    create_thread_response = nexar.get_query(CREATECOMMENTTHREAD_MUTATION, variables)

    errors = create_thread_response["desCreateCommentThread"]["errors"]
    if errors != []:
        print(errors)

    else:
        print("Comment thread successfully created.\n")


def delete_comment_thread(nexar, entityId, commentThreadId):
    print()
    variables = {
        "entityId": entityId,
        "commentThreadId": commentThreadId
    }

    delete_thread_response = nexar.get_query(DELETECOMMENTTHREAD_MUTATION, variables)

    errors = delete_thread_response["desDeleteCommentThread"]["errors"]
    if errors != []:
        print(errors)
    else:
        print("Comment thread successfully deleted.\n")


def update_comment(nexar, entityId, commentThreadId, commentId):
    print()
    text = input("Enter comment... : ")
    variables = {
        "entityId": entityId,
        "commentThreadId": commentThreadId,
        "commentId": commentId,
        "text": text
        }

    updateComment = nexar.get_query(UPDATECOMMENT_MUTATION, variables)
    print()

    if updateComment["desUpdateComment"]["errors"] != []:       # if updateComment is not empty (has an error)
        print(updateComment["desUpdateComment"]["errors"])

    else:
        print("Changes successfully made..." + "\n")


def create_comment(nexar, entityId, commentThreadId):
    print()
    text = input("Enter comment... : ")
    variables = {
        "entityId": entityId,
        "commentThreadId": commentThreadId,
        "text": text
    }

    createComment = nexar.get_query(CREATECOMMENT_MUTATION, variables)
    print()

    if createComment["desCreateComment"]["errors"] != []:       # if createComment is not empty (has an error)
        print(createComment["desCreateComment"]["errors"])

    else:
        print("Comment successfully created..." + "\n")


def delete_comment(nexar, entityId, commentThreadId, commentId):
    print()
    variables = {
        "entityId": entityId,
        "commentThreadId": commentThreadId,
        "commentId": commentId
    }

    deleteComment = nexar.get_query(DELETECOMMENT_MUTATION, variables)

    if deleteComment["desDeleteComment"]["errors"] != []:
        print(deleteComment["desDeleteComment"]["errors"])

    else:
        print("Comment successfully deleted..." + "\n")


if __name__ == '__main__':

    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]
    nexar = NexarClient(client_id, client_secret, ["design.domain", "user.access", "openid"])

    workspaces = get_workspaces(nexar)
    workspace_id = get_workspace_id_from_user(workspaces)

    projects = get_projects(workspace_id, nexar)
    project_id = get_project_id_from_user(projects)

    pcb = get_pcb_from_project(project_id, nexar)
    list_comment_threads(pcb)

    choice = get_user_decision(pcb)
    change_comment(pcb, choice, project_id)
