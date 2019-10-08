import requests, json, os
# URLS
API_BASE = "https://esi.evetech.net/"
KILLS_URL = "v2/universe/system_kills/"
SYSTEM_URL = "v1/universe/systems/"
# Misc
name_range = ['V-OJEN', '49-0LI', 'B-588R', '7-K5EL', 'LZ-6SU', '5ZO-NZ', 'P3EN-E', '0-R5TS', 'FS-RFL', 'H-5GUI',
            'H-UCD1', 'N-HSK0', 'U54-1L', 'Q-EHMJ', 'DAYP-G', '05R-7A', 'G-LOIT', 'YMJG-4', '7-UH4Z', 'KRUN-N',
            'H-NOU5', 'IPAY-2', 'X97D-W', 'EIDI-N', 'HE-V4V', 'PM-DWE', 'FH-TTC', 'NCGR-Q', '4-HWWF', '1N-FJ8',
            'S-NJBB', '2DWM-2', '0R-F2F', 'K8X-6B', '669-IX', 'Q-L07F', 'FMBR-8', 'H-1EOH', 'MQ-O27', 'Y0-BVN',
            '4GYV-Q', 'XSQ-TF', 'A8A-JN', 'MC6O-F', 'X445-5', 'IFJ-EL', '47L-J4', '8TPX-N', 'R-P7KL', 'WBR5-R',
            '6WW-28', 'H-EY0P', 'XF-PWO', 'IR-DYY', 'KX-2UI', '9OO-LH', 'E-D0VZ', 'TVN-FM', 'VI2K-J', '97-M96',
            '0MV-4W', 'C-J7CR', 'F-D49D', 'AZBR-2', 'UNAG-6', 'E-SCTX', '6Y-WRK', '4NGK-F', 'NQ-9IH', 'AP9-LV',
            'KR-V6G', 'MR4-MY', '0-GZX9', '2H-TSE', 'FDZ4-A', 'M-MD31', 'SR-KBB', 'B6-52M', 'L4X-FH', '4K0N-J',
            'WH-2EZ', 'Roua', 'TZL-WT', '2E-ZR5', 'QKTR-L', 'V-MZW0', 'NBPH-N', 'LR-2XT', 'UBX-CC', 'B-F1MI',
            'YN3-E3', 'D0-F4W', 'BND-16', 'O1-FTD', 'L-HV5C', 'IOO-7O', 'BE-UUN', '4-CUM5', 'OEY-OR', 'W-3BSU']

id_range = ['30000208', '30000209', '30000210', '30000211', '30000212', '30000213', '30000214', '30000215', '30000216',
            '30000217', '30000218', '30000219', '30000220', '30000221', '30000222', '30000223', '30000224', '30000225',
            '30000226', '30000227', '30000238', '30000239', '30000240', '30000241', '30000242', '30000243', '30000244',
            '30000245', '30000246', '30000247', '30000248', '30000249', '30000250', '30000251', '30000252', '30000253',
            '30000254', '30000255', '30000256', '30000257', '30000258', '30000259', '30000260', '30000262', '30000263',
            '30000265', '30000268', '30000269', '30000271', '30000273', '30000274', '30000275', '30000276', '30000277',
            '30000279', '30000280', '30000281', '30000282', '30000283', '30000289', '30000290', '30000291', '30000292',
            '30000293', '30000294', '30000295', '30000297', '30002421', '30002422', '30002423', '30002424', '30002425',
            '30002426', '30002427', '30002428', '30002429', '30002430', '30002431', '30002432', '30002433', '30002434',
            '30002435', '30002436', '30002437', '30002438', '30002439', '30002441', '30002451', '30002452', '30002453',
            '30002454', '30002455', '30002456', '30002473', '30002493', '30002494', '30002495', '30002496', '30002497',
            '30002498', ]


def convert_range_to_id():
    with open('system_info.json') as f:
        data = json.load(f)
        for system in data:
            for sys_id in system:
                if system.get(sys_id) in name_range:
                    id_range.append(sys_id)

    with open('id_dump.txt', 'w') as d:
        for sys_id in id_range:
            d.write("'%s', " % sys_id)


def get_sys_name(matched_id):
    """Accepts a list of system IDs and returns a list of system names"""
    sys_names = []
    with open('system_info.json') as f:
        data = json.load(f)
        for system in data:
            for sys_id in system:
                if sys_id in matched_id:
                    return system.get(matched_id)


def system_kill():
    """Accepts a list of systems in range and returns a list of systems with NPC kills at or over the set match_limit"""
    url = API_BASE + KILLS_URL
    jump_range = id_range
    match_limit = 120
    sys_matches = []

    r = requests.get(url=url)
    data = r.json()

    for sys in data:
        if str(sys['system_id']) in jump_range:
            if sys['npc_kills'] >= match_limit:
                # Get name from id match and append with npc kills
                sys_matches.append('{}:{}'.format(get_sys_name(str(sys['system_id'])), str(sys['npc_kills'])))
    # Return names of matches
    return sys_matches


def get_sys_names():
    """Gets all systems in EVE and their corresponding ID then writes it to system_info.json"""
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
    # get_sys_names()
    # convert_range_to_id()
    print(system_kill())
