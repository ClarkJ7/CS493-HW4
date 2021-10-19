from google.cloud import datastore
from flask import Flask, request, Blueprint
import json
import constants
import boats
import loads
import manage

app = Flask(__name__)
app.register_blueprint(boats.bp)
app.register_blueprint(loads.bp)
app.register_blueprint(manage.bp)

client = datastore.Client()

# variable changed for testing/deploying
current_url = constants.google_url


@app.route('/')
def index():
    return 'Please navigate to /boats or /slips to use this API'


@app.route('/reset', methods=['DELETE'])
def reset():
    if request.method == 'DELETE':
        # Clear boats from datastore every reset
        del_query = client.query(kind=constants.boats)
        del_results = list(del_query.fetch())
        for entity in del_results:
            client.delete(entity.key)

        # Clear loads from datastore every reset
        del_query = client.query(kind=constants.loads)
        del_results = list(del_query.fetch())
        for entity in del_results:
            client.delete(entity.key)
        return 'Datastore has been cleared/reset'


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)
