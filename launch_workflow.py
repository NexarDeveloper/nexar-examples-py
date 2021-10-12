"""Example workflow launch with attached files."""
import sys, time
import argparse, json
from nexar_requests import NexarClient

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
    for var in workspace["workflowDefinitions"]: print(var["name"]) 
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
    parser = argparse.ArgumentParser(
      description="Launch a workflow within a workspace. Interacctive prompts for the workflow name and input values."
    )
    parser.add_argument("name", help="The name for the workspace to query.", type=str)
    parser.add_argument("-token", "-t", help="The Nexar access token.", type=str)
    args = parser.parse_args()
    nexar = NexarClient(args.token if (args.token is not None) else sys.stdin.readline().strip())

    variables = {
        "workspace": args.name
    }
    workspace = nexar.get_query(WORKFLOW_VARIABLES, variables)["desWorkspaces"][0]
    workflow = find_workflow(workspace)
        
    variables = {
        "workspace": workspace["url"],
        "workflowDefinition": workflow["workflowDefinitionId"],
        "variables": get_workflow_values(workspace, workflow)
    }
    workflow = nexar.get_query(WORKFLOW_LAUNCH, variables)
    print(json.dumps(workflow["desLaunchWorkflow"], indent = 1))
