import json
import requests
import os
import math
import pandas as pd

#function to list work items from org with pat secret
def list_work_items(organization, pat_secret):
    headers = {'content-type': 'application/json'}
    requestBody = {
        "query": f"Select [System.Id], [System.Title], [System.State] From WorkItems Where [System.Tags] contains 'DevOpsSupportRequest' AND ([System.AreaPath] = 'Cat Digital\CD - Helios' OR [System.AreaPath] = 'Cat Digital\CD - Helios\DevOps') AND [System.WorkItemType] = 'User Story' AND [State] != 'Closed' AND [State] != 'Removed' order by [Microsoft.VSTS.Common.Priority] asc, [System.CreatedDate] desc"
    }
    #devops project name
    project = 'Cat Digital'
    response = requests.post(f"https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=7.1-preview.2", headers=headers, json=requestBody, auth=('', pat_secret))
    if response.status_code == 200:
        return response.json()
    else:
        status_code = response.status_code
        print(f'Error from create_work_item request | Status Code: {status_code}')
        exit(1)

#function to get work item details for specific work item from org with pat secret
def get_work_item(organization, item_id,pat_secret):
    headers = {'content-type': 'application/json'}
    response = requests.get(f"https://dev.azure.com/{organization}/_apis/wit/workitems/{item_id}?api-version=7.0", headers=headers, auth=('', pat_secret))
    if response.status_code == 200:
        return response.json()
    else:
        status_code = response.status_code
        print(f'Error from create_work_item request | Status Code: {status_code}')
        exit(1)

#function to update work item target resolution date from org with pat secret
def update_work_item_assignee(organization, item_id,pat_secret,devOpsEngineer):
    requestBody = [
        {
            "op": "add",
            "path": "/fields/System.AssignedTo",
            "value": devOpsEngineer
        }
    ]
    headers = {
        'content-type': 'application/json-patch+json',
        'dataType': 'application/json-patch+json'
    }
    response = requests.patch(f"https://dev.azure.com/{organization}/_apis/wit/workitems/{item_id}?api-version=7.0", headers=headers, json=requestBody, auth=('', pat_secret))
    if response.status_code == 200:
        return response.json()
    else:
        status_code = response.status_code
        print(f'Error from create_work_item request | Status Code: {status_code}')
        exit(1)

#function to add comment with @mention to the assignee to work item
def addCommentToWorkItem(organization, project, item_id,pat_secret,person1Name,person1Id, person2name, person2Id):
    comment = {"text": f"<div><a href=\"#\" data-vss-mention=\"version:2.0,{person1Id}\">@{person1Name}</a>&nbsp; <a href=\"#\" data-vss-mention=\"version:2.0,{person2Id}\">@{person2name}</a>&nbsp; No DevOps Engineer specified for Team.</div>"}
    headers = {'content-type': 'application/json'}
    response = requests.post(f"https://dev.azure.com/{organization}/{project}/_apis/wit/workItems/{item_id}/comments?api-version=7.0-preview.3", headers=headers, json=comment, auth=('', pat_secret))
    if response.status_code == 200:
        return response.json()
    else:
        status_code = response.status_code
        print(f'Error from create_work_item request | Status Code: {status_code}')
        exit(1)

#function to update work item state to "New" from org with pat secret
def update_work_item_state(organization, item_id,pat_secret):
    requestBody = [
        {
            "op": "add",
            "path": "/fields/System.State",
            "value": "In Analysis"
        }
    ]
    headers = {
        'content-type': 'application/json-patch+json',
        'dataType': 'application/json-patch+json'
    }
    response = requests.patch(f"https://dev.azure.com/{organization}/_apis/wit/workitems/{item_id}?api-version=7.0", headers=headers, json=requestBody, auth=('', pat_secret))
    if response.status_code == 200:
        return response.json()
    else:
        status_code = response.status_code
        print(f'Error from create_work_item request | Status Code: {status_code}')
        exit(1)

#update work item swim lane to "DevOps"
def update_work_item_swim_lane(organization, item_id,pat_secret):
    requestBody = [
        {
            "op": "add",
            "path": "/fields/WEF_E0367B3CE7CE42B29484155CA22D578C_Kanban.Lane",
            "value": "DevOps"
        }
    ]
    headers = {
        'content-type': 'application/json-patch+json',
        'dataType': 'application/json-patch+json'
    }
    response = requests.patch(f"https://dev.azure.com/{organization}/_apis/wit/workitems/{item_id}?api-version=7.0", headers=headers, json=requestBody, auth=('', pat_secret))
    if response.status_code == 200:
        return response.json()
    else:
        status_code = response.status_code
        print(f'Error from create_work_item request | Status Code: {status_code}')
        exit(1)

#function to read txt file as string
def read_txt_file(filename):
    #open text file in read mode
    text_file = open(filename, "r")
    #read whole file to a string
    data = text_file.read()
    #close file
    text_file.close()
    return data

#devops organization name
organization = 'cat-digital'

#define project name
project = 'Cat Digital'

#get PAT_SECRET from github actions secrets
#AZDO_PAT = os.environ.get("AZDO_PAT", "Token not available!")
#AZDO_PAT = read_txt_file("azdo_pat.txt").strip()
os.system('pwd')
os.system('ls')
df_sheet_index = pd.ExcelFile('/AzDO/Automation/devops-engineer-assignment/data.xlsx')
df_sheet = pd.read_excel(df_sheet_index)
team_name_dict = df_sheet.set_index('Team')['2024 DevOps Engineer'].to_dict()
"""
#get user's work items
workItemsList = list_work_items(organization, AZDO_PAT)['workItems']
#loop through all work items and get tags
work_items_needing_alert_list = []

#loop though each work item
for workItem in workItemsList:
    # define work item Id 
    workItemId = workItem["id"]
    #get work item details
    work_item_details = get_work_item(organization, workItemId, AZDO_PAT)
    #get work item fields data
    workItemDetailsFields = work_item_details['fields']
    
    workItemState = workItemDetailsFields["System.State"]
    if "System.Tags" in work_item_details['fields'] :
        work_item_tags_string = work_item_details['fields']["System.Tags"]
        num_tags = work_item_tags_string.count(';')+1
        if(num_tags > 1):
            tags_array = work_item_tags_string.split(';')
            for tag in tags_array:
                tag = tag.strip()
                if tag in team_name_dict:
                    devOpsEngineerName = team_name_dict[tag]
                    if(isinstance(devOpsEngineerName, float)):
                        if math.isnan(devOpsEngineerName):
                            #define person1 to notify for awareness if no devops engineer is specified for the team
                            forAwarenessName1 = 'Minh Ramsden'
                            forAwarenessId1 = '6be5e0e1-3192-63a8-b9bf-71653a1fd120'
                            #define person2 to notify for awareness if no devops engineer is specified for the team
                            forAwarenessName2 = 'SANTHI KOMMURI'
                            forAwarenessId2 = '485e7a5c-c328-627a-8e48-0408597e4dcd'
                            addCommentToWorkItem(organization, project, workItemId, AZDO_PAT, forAwarenessName1, forAwarenessId1, forAwarenessName2, forAwarenessId2)
                            break
                    elif len(devOpsEngineerName) != 0:
                        update_work_item_state(organization, workItemId, AZDO_PAT)
                        update_work_item_assignee(organization, workItemId, AZDO_PAT, devOpsEngineerName)
                        update_work_item_swim_lane(organization, workItemId, AZDO_PAT)
                        break
                    else:
                        print(f'Error in DevOpsEngineer value for team {tag}')
"""

