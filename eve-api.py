import requests, json, os

API_BASE = "https://esi.evetech.net/"
KILLS_URL = "v2/universe/system_kills/"
SYSTEM_URL = "v1/universe/systems/"


def system_kill():
    url = API_BASE + KILLS_URL
    r = requests.get(url=url)
    data = r.json()


def get_sys_names():
    url = API_BASE + SYSTEM_URL
    sys_ids = []
    sys_names = []
    # ID Request
    id_req = requests.get(url=url)
    data = id_req.json()
    for sys_id in data:
        # System Info Request
        name_url = API_BASE + 'v4/universe/systems/%s/' % sys_id
        name_req = requests.get(url=name_url)
        sys_info = name_req.json()
        sys_ids.append(sys_id)
        sys_names.append(sys_info['name'])

    # Zip
    sys_dict = dict(zip(sys_ids, sys_names))
    # Write to json
    with open('system_info_11.json', 'w') as f:
        json.dump(sys_dict, f, indent=4)


if __name__ == '__main__':
    get_sys_names()
