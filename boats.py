from google.cloud import datastore
from flask import Flask, request, Blueprint
import json
import constants


bp = Blueprint('boats', __name__, url_prefix='/boats')
client = datastore.Client()


@bp.route('', methods=['GET', 'POST'])
def boats():
    # return all boats
    if request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for boat in results:
            boat["id"] = boat.key.id
        return json.dumps(results)

    # add boat to client
    elif request.method == 'POST':
        # get body from request
        content = request.get_json()
        # check for all attributes
        if 'name' not in content:
            return constants.boatAtt_err, 400
        elif 'type' not in content:
            return constants.boatAtt_err, 400
        elif 'length' not in content:
            return constants.boatAtt_err, 400
        # add boat to client
        else:
            new_boat = datastore.Entity(client.key(constants.boats))
            new_boat.update(
                {"name": content["name"],
                 "type": content["type"],
                 "length": content["length"],
                 "loads": []
                 })
            client.put(new_boat)
            # add id and self attributes for response
            new_boat["id"] = new_boat.key.id
            new_boat["self"] = constants.current_url + "boats/" + str(new_boat.key.id)
            return new_boat, 201
    # invalid method used
    else:
        return 'Invalid request method, please try again'


@bp.route('/<boat_id>', methods=['GET', 'PATCH', 'DELETE'])
def boat(boat_id):
    boat_key = client.key(constants.boats, int(boat_id))
    boat = client.get(key=boat_key)
    # check for boat_id
    if boat is None:
        return constants.boatID_err, 404
    # return specified boat
    if request.method == 'GET':
        # add id and self attributes for response
        boat["id"] = boat.key.id
        boat["self"] = constants.current_url + "boats/" + str(boat.key.id)
        return json.dumps(boat)

    # modify specified boat
    elif request.method == 'PATCH':
        # get body from request
        content = request.get_json()
        # check for all attributes
        if 'name' not in content:
            return constants.boatAtt_err, 400
        elif 'type' not in content:
            return constants.boatAtt_err, 400
        elif 'length' not in content:
            return constants.boatAtt_err, 400
        else:
            boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
            client.put(boat)
            # add id and self attributes for response
            boat["id"] = boat.key.id
            boat["self"] = constants.current_url + "boats/" + str(boat.key.id)
            return json.dumps(boat)

    # delete specified boat from client
    elif request.method == 'DELETE':
        client.delete(boat_key)

        # Add functionality to free up loads on deleted boat
        """
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for slip in results:
            # if boat_id is found at slip, remove it
            if slip["current_boat"] == int(boat_id):
                target_key = client.key(constants.slips, slip.key.id)
                slip_get = client.get(key=target_key)
                slip_get.update({"number": slip["number"], "current_boat": None})
                client.put(slip_get)
                break
        """
        return '', 204
