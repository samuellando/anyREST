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
        return {"code": 404}, 404

    for k in elem:
        try:
            int(k)
        except:
            return elem

    return json.dumps(list(elem.values()))

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
                    "code": 400, 
                    "message": "Endpoint is not a collection",
                    "description": "Not all existing keys in enpoint are ints.",
                    }, 400
    else:
        id = "0"

    new["id"] = int(id)
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
        return {"code": 404}, 404

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
        return {"code": 404}, 404

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
        return {"code": 404}, 404

    col[layers[-1]] = None

    saveData(data)

    return {"code": 204}, 204

@app.after_request
def after_request_func(response):
    """
    Apply the global options.
    """

    data = json.loads(response.get_data())

    # Filtering.
    if type(data) is list:
        for f in request.args:
            # Exclude the other params
            if f in ['pretty', 'fields']:
                continue
            new = []
            for e in data:
                if str(e.get(f)) == request.args[f]:
                        new.append(e)
            data = new

    # Only include certain feilds in the output.
    fields = request.args.get('fields')
    if fields != None:
        fields = fields.split(",")
        if type(data) is dict:
            new = [data]
        else:
            new = data
        for i in range(len(new)):
            e = {}
            for f in fields:
                if f in new[i]:
                    e[f] = new[i][f]
            new[i] = e

        print(new)
        if type(data) is dict:
            data = new[0]
        else:
            data = new

    # Pretty print the json.
    pretty = request.args.get('pretty')
    if pretty == "true":
        response.set_data(json.dumps(data, indent=2))
    else:
        response.set_data(json.dumps(data))

    return response

