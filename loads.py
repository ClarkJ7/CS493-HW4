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
        inp_limit = request.args.get("limit", 3)
        inp_offset = request.args.get("page", 0)
        query_iter = query.fetch(limit=inp_limit, offset=inp_offset)
        pages = query_iter.pages
        results = list(next(pages))
        if query_iter.next_page_token:
            next_offset = int(inp_offset) + int(inp_limit)
            next_url = request.base_url + "?limit=" + str(inp_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None
        for e in results:
            e["id"] = e.key.id
        output = {"loads": results}
        if next_url:
            output["next"] = next_url
        return json.dumps(output)

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
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for boat in results:
            temp_load = []
            check = len(boat["loads"])
            # if load_id is found in boat, remove it
            # iterate through loads
            for load in boat["loads"]:
                if load["id"] == int(load_id):
                    target_key = client.key(constants.boats, boat.key.id)
                    boat_get = client.get(key=target_key)
                    boat_get.update(
                        {"name": boat_get["name"],
                         "type": boat_get["type"],
                         "length": boat_get["length"],
                         "loads": temp_load
                         })
                else:
                    temp_load.append(load)
            if check != len(temp_load):
                client.put(boat_get)
                return '', 204

        return '', 204
