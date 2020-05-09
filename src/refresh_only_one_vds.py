import requests
import re
import json

# INPUT:
# copy vds path from UI, click Copy Path
dataset_path = 'test.delays'

dremio_url = 'http://localhost:9047'  # url dremio
user = "viktor"  # user name in dremio
pwd = "dremio123"  # password ame in dremio
verify_ssl = False  # SSL enanled/disabled for REST calls

#######################

token = "_dremio"
content_type = "application/json"


def reenable_reflection(refl_json):
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    data = refl_json

    key_to_remove = ['updatedAt', 'createdAt',
                     'currentSizeBytes', 'totalSizeBytes']
    for key in key_to_remove:
        data.pop(key)

    refl_id = data['id']
    data['enabled'] = False
    data = json.dumps(data)

    # disable reflesction
    res = requests.put(dremio_url + '/api/v3/reflection/' +
                       refl_id, headers=headers, data=data, verify=verify_ssl)

    # get new tag version for update
    res = requests.get(
        dremio_url + '/api/v3/reflection/'+refl_id, headers=headers, verify=verify_ssl)
    data = res.json()

    for key in key_to_remove:
        data.pop(key)
    data['enabled'] = True
    data = json.dumps(data)

    # enable reflection, will trigger an update
    requests.put(dremio_url + '/api/v3/reflection/' +
                 refl_id, headers=headers, data=data, verify=verify_ssl)


def get_vds_id_by_path(path):
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    dataset_obj = {}
    try:
        response = requests.get(
            dremio_url + '/api/v3/catalog/by-path' + path, headers=headers, verify=verify_ssl)
        dataset_obj = {"res": True, "id": response.json(
        )["id"], "type": response.json()["type"]}
        return dataset_obj
    except requests.exceptions.SSLError as e:
        print("SSLError")
        dataset_obj = {"res": False, "id": None, "type": e}
        return dataset_obj


def get_all_reflections():
    headers = {'Content-Type': 'application/json', 'Authorization': token}
    return requests.get(
        dremio_url + '/api/v3/reflection', headers=headers, verify=verify_ssl)


def parse_dataset_path(dataset_path):
    path = ""
    dataset_path = re.findall('"[^"]*"|[^.]+', dataset_path)
    dataset_path = [dataset_path_part.replace(
        '"', '') for dataset_path_part in dataset_path]
    dataset_path = [dataset_path_part.replace(
        ' ', '%20') for dataset_path_part in dataset_path]
    for part in dataset_path:
        path = path+"/"+part
    return (path)


def login():
    headers = {'Content-Type': content_type}
    data = '{"userName": "' + user + '","password": "'+pwd+'" }'
    token_obj = {}
    try:
        response = requests.post(
            dremio_url + '/apiv2/login', headers=headers, data=data, verify=verify_ssl)
        token = response.json()['token']  # _dremio is prepended to the token
        token_obj = {"res": True, "token": token}
        return token_obj
    except requests.exceptions.SSLError as e:
        print("SSLError")
        token_obj = {"res": False, "token": e}
        return token_obj


if __name__ == "__main__":
    token_obj = login()
    if (token_obj["res"]):
        token = token+token_obj["token"]
        dataset_id = get_vds_id_by_path(parse_dataset_path(dataset_path))['id']

        response = get_all_reflections()

        reflections = response.json()
        for reflection in reflections['data']:
            if dataset_id == reflection['datasetId']:
                if reflection['enabled'] == True:
                    reenable_reflection(reflection)
