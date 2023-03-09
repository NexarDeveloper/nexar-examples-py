from nexarClients.design.nexarDesignClient import NexarClient
import os
import csv

FILTER1 = "Filter by inputted parameter equal to inputted value"
FILTER2 = "Filter by inputted parameter not equal to inputted value"
FILTER3 = "Filter by inputted parameter that starts with inputted value"
ALL = "Write all components to csv file"

FILTER_TYPES = [ALL, FILTER1, FILTER2, FILTER3]

LIBRARY_COMPONENTS_QUERY = '''
query GetLibrary($workspaceUrl : String!) {
    desLibrary(
        workspaceUrl: $workspaceUrl
    ) {
        components{
            nodes{
                id
                name
                description
                comment
                manufacturerParts{
                    companyName
                    partNumber
                    priority
                }
                details{
                    parameters{
                        name
                        value
                        type
                    }
                }
            }
        }
    }
}
'''


def get_user_decision():

    print()
    for index, item in enumerate(FILTER_TYPES):
        print(index + 1, ":", item)

    print()
    userPageDecision = input("Enter number to filter by... : ")
    userPageDecision = int(userPageDecision)

    if userPageDecision <= 0 or userPageDecision > len(FILTER_TYPES):
        print("\n" + "Invalid response, try again... ")
        return get_user_decision()
    else:
        return FILTER_TYPES[userPageDecision - 1]


def get_parts(userDecision, libraryComponents):

    parts = []
    print()

    if userDecision != ALL:

        filterName = input("Enter parameter name to filter by... : ")
        print()
        filterValue = input("Enter filter value... : ")
        print()

    if userDecision == FILTER1:
        libraryComponents = apply_filter1(libraryComponents, filterName, filterValue, parts)

    elif userDecision == FILTER2:
        libraryComponents = apply_filter2(libraryComponents, filterName, filterValue, parts)

    elif userDecision == FILTER3:
        libraryComponents = apply_filter3(libraryComponents, filterName, filterValue, parts)

    parts = convert_components(libraryComponents)

    return parts


def apply_filter1(libraryComponents, filterName, filterValue, parts):

    for component in libraryComponents:

        parameterList = [p for p in component["details"]["parameters"] if p["name"].lower() == filterName.lower()]

        if len(parameterList) != 0:

            parameter = next(iter(parameterList))

            if parameter["value"].lower() == filterValue.lower():  # checks if parameter value is inputted value
                parts.append(component)

    if parts == []:
        print("No parameters with", filterValue, "were found...")
    return parts


def apply_filter2(libraryComponents, filterName, filterValue, parts):

    for component in libraryComponents:

        parameterList = [p for p in component["details"]["parameters"] if p["name"].lower() == filterName.lower()]

        if len(parameterList) != 0:

            parameter = next(iter(parameterList))

            if parameter["value"].lower() != filterValue.lower():  # checks if parameter value is not inputted value
                parts.append(component)

    if parts == []:
        print("No parameters with", filterName, "not being", filterValue, "were found...")
    return parts


def apply_filter3(libraryComponents, filterName, filterValue, parts):

    for component in libraryComponents:

        parameterList = [p for p in component["details"]["parameters"] if p["name"].lower() == filterName.lower()]

        if len(parameterList) != 0:

            parameter = next(iter(parameterList))

            # checks if parameter value starts with inputted value
            if parameter["value"].lower().startswith(filterValue.lower()):
                parts.append(component)

    if parts == []:
        print("No parameters that start with", filterValue, "were found...")
    return parts


def convert_components(libraryComponents):

    parts = []
    for component in libraryComponents:

        if component["manufacturerParts"] == []:
            for parameterIndex in range(len(component["details"]["parameters"])):

                returned = convert_to_csv_format(component, parameterIndex, 0)
                del returned["details"], returned["manufacturerParts"]
                parts.append(returned)
        else:
            for manufacturerIndex in range(len(component["manufacturerParts"])):

                for parameterIndex in range(len(component["details"]["parameters"])):

                    returned = convert_to_csv_format(component, parameterIndex, manufacturerIndex)
                    del returned["details"], returned["manufacturerParts"]
                    parts.append(returned)

    return parts


def convert_to_csv_format(component, parameterIndex, manufacturerIndex):

    component = component.copy()

    if component["manufacturerParts"] != []:

        component["companyName"] = component["manufacturerParts"][manufacturerIndex]["companyName"]
        component["partNumber"] = component["manufacturerParts"][manufacturerIndex]["partNumber"]
        component["priority"] = component["manufacturerParts"][manufacturerIndex]["priority"]

    else:
        component["companyName"] = None
        component["partNumber"] = None
        component["priority"] = None

    if component["details"]["parameters"] is not None:

        component["parametersName"] = component["details"]["parameters"][parameterIndex]["name"]
        component["value"] = component["details"]["parameters"][parameterIndex]["value"]
        component["type"] = component["details"]["parameters"][parameterIndex]["type"]

    else:
        component["parametersName"] = None
        component["value"] = None
        component["type"] = None

    return component


if __name__ == '__main__':

    client_id = os.environ["NEXAR_CLIENT_ID"]
    client_secret = os.environ["NEXAR_CLIENT_SECRET"]

    nexar = NexarClient(client_id, client_secret, ["design.domain", "user.access", "offline_access"])

    workspaceUrl = input("\n" + "Enter your workspace URL... : ")

    variables = {
        "workspaceUrl": workspaceUrl
    }

    libraryComponents = nexar.get_query(LIBRARY_COMPONENTS_QUERY, variables)["desLibrary"]["components"]["nodes"]

    userDecision = get_user_decision()
    parts = get_parts(userDecision, libraryComponents)

    if parts != []:

        with open('library_components.csv', 'w', newline="") as componentsCsv:

            writer = csv.DictWriter(componentsCsv, fieldnames=[
                "id",
                "name",
                "description",
                "comment",
                "companyName",
                "partNumber",
                "priority",
                "parametersName",
                "value",
                "type"], extrasaction='ignore')

            writer.writeheader()
            writer.writerows(parts)

    else:

        print("No data to write to CSV file...")
