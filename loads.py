from google.cloud import datastore
from flask import Flask, request, Blueprint
import json
import constants
from datetime import date

bp = Blueprint('loads', __name__, url_prefix='/loads')
client = datastore.Client()


@bp.route('', methods=['GET', 'POST'])
def loads():
    # return all loads
    if request.method == 'GET':
        query = client.query(kind=constants.loads)
        results = list(query.fetch())
        for load in results:
            load["id"] = load.key.id
        return json.dumps(results)

    # add boat to client
    elif request.method == 'POST':
        today = date.today()
        # get body from request
        content = request.get_json()
        # check for all attributes
        if 'volume' not in content:
            return constants.loadAtt_err, 400
        elif 'content' not in content:
            return constants.loadAtt_err, 400
        # add load to client
        else:
            new_load = datastore.Entity(client.key(constants.loads))
            new_load.update(
                {"volume": content["volume"],
                 "carrier": None,
                 "content": content["content"],
                 "creation_date": today.strftime('%m/%d/%Y')
                 })
            client.put(new_load)
            # add id and self attributes for response
            new_load["id"] = new_load.key.id
            new_load["self"] = constants.current_url + "loads/" + str(new_load.key.id)
            return new_load, 201

    # invalid method used
    else:
        return 'Invalid request method, please try again'


@bp.route('/<load_id>', methods=['GET', 'PATCH', 'DELETE'])
def load(load_id):
    load_key = client.key(constants.loads, int(load_id))
    load = client.get(key=load_key)
    # check for boat_id
    if load is None:
        return constants.loadID_err, 404
    # return specified boat
    if request.method == 'GET':
        # add id and self attributes for response
        load["id"] = load.key.id
        load["self"] = constants.current_url + "loads/" + str(load.key.id)
        return json.dumps(load)

    # modify specified boat
    elif request.method == 'PATCH':
        # get body from request
        content = request.get_json()
        # check for all attributes
        if 'volume' not in content:
            return constants.loadAtt_err, 400
        elif 'content' not in content:
            return constants.loadAtt_err, 400
        else:
            load.update({"name": content["name"], "type": content["type"], "length": content["length"]})
            client.put(load)
            # add id and self attributes for response
            load["id"] = load.key.id
            load["self"] = constants.current_url + "loads/" + str(load.key.id)
            return json.dumps(load)

    # delete specified boat from client
    elif request.method == 'DELETE':
        client.delete(load_key)

        # Add functionality to free up boats carrying deleted load
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
