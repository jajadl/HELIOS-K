import hapi

def get_global_ids(molecule):
    global_ids = []
    for key in hapi.ISO:
        if molecule == hapi.ISO[key][-1]:
            global_ids.append(hapi.ISO[key][0])
            print(f"Found global ID {hapi.ISO[key][0]} for {molecule}")
    return global_ids

get_global_ids('OCS')