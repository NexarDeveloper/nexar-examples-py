from nexar_requests import NexarClient
import sys
from design_helpers import (
    get_workspaces,
    get_workspace_id_from_user,
    get_projects,
    get_project_id_from_user
)

UPDATE_ACTION = "Update comment"
CREATE_ACTION = "Create comment"
DELETE_ACTION = "Delete comment"

COMMENT_ACTIONS = [UPDATE_ACTION, CREATE_ACTION, DELETE_ACTION]

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

def get_user_decision(commentThreads):
    if commentThreads == []:                                    # if there are no comments
        print("No comment to update, or thread to add to...")
        sys.exit()
    
    for index, item in enumerate(COMMENT_ACTIONS):
        print(index + 1, ":", item)
    
    print()
    choice = input("Enter number to update, create or delete a comment... : ")
    choice = int(choice)
    print()
   
    if choice <= 0 or choice > len(COMMENT_ACTIONS):
        print("Invalid response, try again... " + "\n")
        get_user_decision(commentThreads)
    
    return COMMENT_ACTIONS[choice-1]

def change_comment(commentThreads, choice, entityId):
    if choice == CREATE_ACTION:
        commentThreadId = input("Enter comment thread ID for the section you want to add a comment to... : ")
        create_comment(nexar, entityId, commentThreadId)        
    
    else:
        if choice == UPDATE_ACTION:
            currentText = "Enter comment ID for the comment you want to change... : "
        
        elif choice == DELETE_ACTION:
            currentText = "Enter comment ID for the comment you want to delete... : "
        
        commentId = input(currentText)
        commentThreadId = ""
        
        for commentThread in commentThreads:
            
            for comments in commentThread["comments"]:                     # gets commentThreadId from commentId
                
                if comments["commentId"] == commentId:
                    commentThreadId = commentThread["commentThreadId"]
        
        if commentThreadId == "":                               # if the for loop could not find a commentThreadId, meaning the comment ID used was invalid
            print("\n" + "Invalid Comment ID..." + "\n")
            change_comment(commentThreads, choice, entityId)                   # loops until correct comment ID is used
        
        if choice == UPDATE_ACTION:
            update_comment(nexar, entityId, commentThreadId, commentId)  
        
        else:
            delete_comment(nexar, entityId, commentThreadId, commentId)  

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
    token = input("Enter token : ")
    nexar = NexarClient(token)

    workspaces = get_workspaces(nexar)
    workspace_id = get_workspace_id_from_user(workspaces)

    projects = get_projects(workspace_id, nexar)
    project_id = get_project_id_from_user(projects)

    commentThreads = get_comment_threads_from_project(project_id, nexar)
    list_comment_threads(commentThreads)

    choice = get_user_decision(commentThreads)
    change_comment(commentThreads, choice, project_id)