from flask import Flask, request, Response
from markupsafe import escape
import json

app = Flask(__name__)

def loadData():
    with open("data.json", "r") as f:
        data = json.load(f)
    return data 

def saveData(data):
    with open("data.json", "w") as f:
        f.write(json.dumps(data))

def getByKeys(data, keys):
    for k in keys:
        if k in data:
            data = data[k]
        else:
            return None
    
    return data

@app.route("/v1/<path:path>", methods=["GET"])
def get(path):
    """
    Get an object, or set of objects.
    """
    layers = path.split("/")

    data = loadData()

    elem = getByKeys(data, layers)

    if elem == None:
        return "", 404

    return elem

@app.route("/v1/<path:path>", methods=["POST"])
def post(path):
    """
    Create a new object.
    """
    new = request.json

    layers = path.split("/")

    data = loadData()
    p = data

    parents = {}
    for l in reversed(layers):
        parents = {l: parents}

    for l in layers:
        if l in p:
            parents = parents[l]
            p = p[l]
        else:
            p[l] = parents[l]
            break

    col = data
    for l in layers:
        col = col[l]

    if len(col.keys()) > 0:
        try:
            id = str(max(map(lambda x:int(x), col.keys())) + 1)
        except ValueError:
            return { 
                    "code": 1, 
                    "message": "Endpoint is not a collection",
                    "description": "Not all existing keys in enpoint are ints.",
                    }, 400
    else:
        id = "0"

    new["id"] = id
    col[id] = new 

    saveData(data)

    res = Response(json.dumps(new))

    res.headers['location'] = "/"+path+"/"+id

    return res, 201

@app.route("/v1/<path:path>", methods=["PUT"])
def put(path):
    """
    fully update an object.
    """
    update = request.json

    layers = path.split("/")

    data = loadData()

    col = getByKeys(data, layers[:-1])

    if col == None or not layers[-1] in col or col[layers[-1]] == None:
        return "", 404

    col[layers[-1]] = update

    saveData(data)

    return update, 200

@app.route("/v1/<path:path>", methods=["PATCH"])
def patch(path):
    """
    Partially update an object
    """
    update = request.json

    layers = path.split("/")

    data = loadData()

    elem = getByKeys(data, layers)

    if elem == None:
        return "", 404

    for key in update:
        elem[key] = update[key]

    saveData(data)

    return elem, 200

@app.route("/v1/<path:path>", methods=["DELETE"])
def delete(path):
    layers = path.split("/")

    data = loadData()

    col = getByKeys(data,layers[:-1])

    if col == None or not layers[-1] in col or col[layers[-1]] == None:
        return "", 404

    col[layers[-1]] = None

    saveData(data)

    return "", 204

@app.after_request
def after_request_func(response):
    pretty = request.args.get('pretty')
    if pretty == "true":
        data = json.loads(response.get_data())
        response.set_data(json.dumps(data, indent=2))
    return response

