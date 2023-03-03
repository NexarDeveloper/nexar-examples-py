import sys
import os
from nexarClients.design.nexarDesignClient import NexarClient
from nexarClients.design.design_helpers import (
    get_workspaces,
    get_workspace_id_from_user,
    get_projects,
    get_project_id_from_user
)

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


def get_component_info_for_project(project_id, nexar):
    queryAmount = 25

    variables = {
        "projectId": project_id,
        "queryAmount": queryAmount
    }

    componentInfoForProject = nexar.get_query(
        GETCOMPONENTINFOFORPROJECT_QUERY, variables
        )["desProjectById"]["design"]["workInProgress"]["variants"]
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

            if designItem["component"] is not None:
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
    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]
    nexar = NexarClient(client_id, client_secret, ["design.domain", "user.access", "openid"])

    workspaces = get_workspaces(nexar)
    workspace_id = get_workspace_id_from_user(workspaces)

    projects = get_projects(workspace_id, nexar)
    project_id = get_project_id_from_user(projects)

    componentInfo = get_component_info_for_project(project_id, nexar)
    list_component_info_for_project(componentInfo)
