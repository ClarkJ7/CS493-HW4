from google.cloud import datastore
from flask import Flask, request, Blueprint
import json
import constants


bp = Blueprint('manage', __name__, url_prefix='/')
client = datastore.Client()


@bp.route('boats/<boat_id>/loads/<load_id>', methods=['PUT', 'DELETE'])
def manage(boat_id, load_id):
    # get specified boat
    boat_key = client.key(constants.boats, int(boat_id))
    boat = client.get(key=boat_key)

    # get specified boat
    load_key = client.key(constants.loads, int(load_id))
    load = client.get(key=load_key)

    # check for boat_id
    if boat is None:
        return constants.invalidID_err, 404
    else:
        boat_val = {"id": boat.key.id,
                    "name": boat["name"],
                    "self": constants.current_url + "boats/" + str(boat.key.id)}
    # check for slip_id
    if load is None:
        return constants.invalidID_err, 404
    else:
        load_val = {"id": load.key.id,
                    "self": constants.current_url + "loads/" + str(load.key.id)}

    if request.method == 'PUT':
        # check if slip is empty
        if load["carrier"] is not None:
            return constants.loadCar_err, 403
        else:
            # update load carrier
            load.update(
                {"volume": load["volume"],
                 "carrier": boat_val,
                 "content": load["content"],
                 "creation_date": load["creation_date"]
                 })

            # update boat loads CHECK IF THIS WORKS
            if boat["loads"] is None:
                load_boat = [load_val]
            else:
                load_boat = []
                for i in boat["loads"]:
                    load_boat.append(i)
                load_boat.append(load_val)

            boat.update(
                {"name": boat["name"],
                 "type": boat["type"],
                 "length": boat["length"],
                 "loads": load_boat
                 })
            client.put_multi([load, boat])
            return '', 204

    elif request.method == 'DELETE':
        if load["carrier"] is None:
            return constants.wrongBoat_err, 403
        elif load_val not in boat["loads"]:
            return constants.wrongBoat_err, 403
        else:
            # update load carrier
            load.update(
                {"volume": load["volume"],
                 "carrier": None,
                 "content": load["content"],
                 "creation_date": load["creation_date"]
                 })

            # update boat loads CHECK IF THIS WORKS
            if len(boat["loads"]) == 1:
                load_boat = None
            else:
                load_boat = []
                for i in boat["loads"]:
                    if i["id"] == boat_val["id"]:
                        continue
                    else:
                        load_boat.append(i)

            boat.update(
                {"name": boat["name"],
                 "type": boat["type"],
                 "length": boat["length"],
                 "loads": load_boat
                 })
            client.put_multi([load, boat])
            return '', 204

    else:
        return 'Invalid request method, please try again'
