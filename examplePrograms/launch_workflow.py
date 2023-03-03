"""Example workflow launch with attached files."""
import os
import time
import json
from nexarClients.design.nexarDesignClient import NexarClient

WORKFLOW_VARIABLES = """
query Workflow($workspace: String!) {
  desWorkspaces(where: {name: {eq: $workspace}}) {
    url
    workflowDefinitions {
      name
      workflowDefinitionId
      variables {
        name
        valueType
      }
    }
  }
}"""
WORKFLOW_LAUNCH = """
mutation Workflow($workspace: String!, $workflowDefinition: String!, $variables: [DesWorkflowVariableInput!]!) {
  desLaunchWorkflow(input:{
    workspaceUrl: $workspace,
    workflowDefinitionId: $workflowDefinition,
    name: "This is optional",
    variables: $variables}) {
    id
  }
}"""


def find_workflow(workspace):
    for var in workspace["workflowDefinitions"]:
        print(var["name"])
    workflowName = input("Enter workflow name: ")

    workflow = next((p for p in workspace["workflowDefinitions"] if (p["name"] == workflowName)), None)
    if (workflow is None):
        print("No workflow found with that name")
        raise SystemExit

    return workflow


def get_workflow_values(workspace, workflow):
    values = []
    for v in workflow["variables"]:
        values.append({"name": v["name"], "value": input("Value for {}: ".format(v["name"]))})
        if (v["valueType"] == "attachment" and len(values[-1]["value"])):
            container = str(time.time_ns()) + "-Attachment"
            upload = [
                nexar.upload_file(
                    workspace["url"],
                    path.strip(),
                    container
                ) for path in values[-1]["value"].split(",")
            ]
            values[-1]["value"] = ",".join(upload)

    return values


if __name__ == '__main__':

    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]
    nexar = NexarClient(client_id, client_secret, ["design.domain", "user.access", "offline_access"])

    workspaceName = input("\n" + "Enter your workspace name: ")

    variables = {
        "workspace": workspaceName
    }

    print(nexar.get_query(WORKFLOW_VARIABLES, variables))
    workspace = nexar.get_query(WORKFLOW_VARIABLES, variables)["desWorkspaces"][0]
    workflow = find_workflow(workspace)

    variables = {
        "workspace": workspace["url"],
        "workflowDefinition": workflow["workflowDefinitionId"],
        "variables": get_workflow_values(workspace, workflow)
    }
    workflow = nexar.get_query(WORKFLOW_LAUNCH, variables)
    print(json.dumps(workflow["desLaunchWorkflow"], indent=1))
