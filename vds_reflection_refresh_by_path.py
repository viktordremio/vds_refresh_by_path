import requests
import re

#INPUT: 
dataset_path = 'test."concat test limit.20"' #copy vds path from UI, click Copy Path

dremio_url = 'http://localhost:9047' # url dremio
user="user" # user name in dremio
pwd="pwd" # password ame in dremio
verify_ssl=False # SSL enanled/disabled for REST calls

#######################

token = "_dremio"
content_type = "application/json"

def recursive(datasets):
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    for dataset in datasets:
        response = requests.get(dremio_url + '/api/v3/catalog/'+ dataset['id'] +'/graph', headers=headers,verify=False)
        graph(response.json()['parents'])

def graph(parents):
    datasets=[]
    for parent in parents:
        if (parent['datasetType']=='VIRTUAL'):
            datasets.append({"id": parent['id']})
        else:
            refresh_pds(parent["id"])
        break
    recursive(datasets)    

def refresh_pds(id):
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    data=""
    try:
        response = requests.post(dremio_url + '/api/v3/catalog/'+ id +'/refresh', headers=headers, data=data, verify=verify_ssl)
        print("done")
    except requests.exceptions.SSLError as e:
        print("SSLError")

def get_vds_id_by_path(path):
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    dataset_obj={}
    try:
        response = response = requests.get(dremio_url + '/api/v3/catalog/by-path'+ path, headers=headers,verify=verify_ssl)
        dataset_obj={"res":True, "id":response.json()["id"], "type":response.json()["type"] }
        return dataset_obj
    except requests.exceptions.SSLError as e:
        print("SSLError")
        dataset_obj={"res":False, "id":None, "type":None}
        return dataset_obj

def parse_dataset_path(dataset_path):
    path=""
    dataset_path = re.findall('"[^"]*"|[^.]+', dataset_path)
    dataset_path = [dataset_path_part.replace('"', '') for dataset_path_part in dataset_path]
    dataset_path = [dataset_path_part.replace(' ', '%20') for dataset_path_part in dataset_path]
    for part in dataset_path:
        path=path+"/"+part
    return (path)

def login():
    headers = {'Content-Type': content_type}
    data = '{"userName": "'+ user + '","password": "'+pwd+'" }'
    token_obj={}
    try:
        response = requests.post(dremio_url + '/apiv2/login', headers=headers, data=data, verify=verify_ssl)
        token = response.json()['token'] # _dremio is prepended to the token
        token_obj={"res":True, "token":token}
        return token_obj
    except requests.exceptions.SSLError as e:
        print("SSLError")
        token_obj={"res":False, "token":None}
        return token_obj


if __name__ == "__main__":
    token_obj=login()
    datasets=[]
    if (token_obj["res"]):
        token=token+token_obj["token"]
        path=parse_dataset_path(dataset_path)
        datasets.append({"id":get_vds_id_by_path(path)["id"], "type": get_vds_id_by_path(path)["id"]})
        recursive(datasets)




