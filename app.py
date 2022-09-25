from flask import Flask, request, Response
from markupsafe import escape
import json
import secrets
import time

app = Flask(__name__)

DATA_DIR = "data"
META_DATA = "meta.json"

def getMeta():
    global META_DATA
    with open(META_DATA, "r") as f:
        data = json.load(f)
    return data 

def setMeta(data):
    global META_DATA
    with open(META_DATA, "w") as f:
        f.write(json.dumps(data))

def loadData(token):
    global DATA_DIR
    meta = getMeta()
    if not token in meta:
        return {}
    with open(DATA_DIR+"/"+token+".json", "r") as f:
        data = json.load(f)
    return data 

def saveData(token, data):
    global DATA_DIR
    meta = getMeta()
    if not token in meta:
        return
    meta[token]["lastModified"] = time.time_ns()
    setMeta(meta)
    with open(DATA_DIR+"/"+token+".json", "w") as f:
        f.write(json.dumps(data))

def getByKeys(data, keys):
    for k in keys:
        if k in data:
            data = data[k]
        else:
            return None
    
    return data

@app.route("/new", methods=["GET"])
def new():
    return 'CREATE A NEW TOKEN'

@app.route("/new", methods=["POST"])
def createNew():
    meta = getMeta()
    token = secrets.token_urlsafe(16)
    while token in meta:
        token = secrets.token_urlsafe(16)
    meta[token] = {"lastModified": time.time_ns()}
    setMeta(meta)
    saveData(token, {})
    return token


@app.route("/v1/<token>/<path:path>", methods=["GET"])
def get(path, token):
    """
    Get an object, or set of objects.
    """
    layers = path.split("/")

    data = loadData(token)

    elem = getByKeys(data, layers)

    if elem == None:
        return {"code": 404}, 404

    for k in elem:
        try:
            int(k)
        except:
            return elem

    return json.dumps(list(elem.values()))

@app.route("/v1/<token>/<path:path>", methods=["POST"])
def post(path, token):
    """
    Create a new object.
    """
    new = request.json

    layers = path.split("/")

    data = loadData(token)
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

    saveData(token, data)

    res = Response(json.dumps(new))

    res.headers['location'] = "/"+path+"/"+id

    return res, 201

@app.route("/v1/<token>/<path:path>", methods=["PUT"])
def put(path, token):
    """
    fully update an object.
    """
    update = request.json

    layers = path.split("/")

    data = loadData(token)

    col = getByKeys(data, layers[:-1])

    if col == None or not layers[-1] in col or col[layers[-1]] == None:
        return {"code": 404}, 404

    col[layers[-1]] = update

    saveData(token, data)

    return update, 200

@app.route("/v1/<token>/<path:path>", methods=["PATCH"])
def patch(path, token):
    """
    Partially update an object
    """
    update = request.json

    layers = path.split("/")

    data = loadData(token)

    elem = getByKeys(data, layers)

    if elem == None:
        return {"code": 404}, 404

    for key in update:
        elem[key] = update[key]

    saveData(token, data)

    return elem, 200

@app.route("/v1/<token>/<path:path>", methods=["DELETE"])
def delete(path, token):
    layers = path.split("/")

    data = loadData(token)

    col = getByKeys(data,layers[:-1])

    if col == None or not layers[-1] in col or col[layers[-1]] == None:
        return {"code": 404}, 404

    del col[layers[-1]]

    saveData(token, data)

    return {"code": 204}, 204

@app.after_request
def after_request_func(response):
    """
    Apply the global options.
    """
    try:
        data = json.loads(response.get_data())
    except:
        return response


    # Filtering (lists).
    if type(data) is list:
        for f in request.args:
            # Exclude the other params
            if f in ['pretty', 'fields','sort']:
                continue
            new = []
            for e in data:
                if str(e.get(f)) == request.args[f]:
                        new.append(e)
            data = new

    # Sorting (lists).
    sorts = request.args.get('sort')
    if sorts != None and type(data) is list:
        sorts = sorts.split(",")

        keys = getKeys(data, sorts)

        print(keys)

        for i in range(len(data)):
            data[i] = [keys[i], data[i]]

        data.sort(key=lambda e : e[0])

        for i in range(len(data)):
            data[i] = data[i][1]


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

def getKeys(data, sorts):
    keys = [()] * len(data)
    for sort in sorts:
        # Check if all types match.
        match = True
        t = None
        for e in data:
            if sort in e:
                if t == None:
                    t = type(e[sort])
                else:
                    if t != type(e[sort]):
                        match = False
                        break
            
        # Set the default value.
        if t is None:
            continue
        elif t is int or t is float:
            default = 0
        elif t is str:
            default = ""
        elif t is list:
            defualt = []
        elif t is bool:
            default = False
        else: # dict, ...
            match = False

        if match:
            f = lambda e : e[sort] if sort in e else default
        else:
            f = lambda e : str(e[sort]) if sort in e else ""

        for i in range(len(data)):
            keys[i] = (*keys[i], f(data[i]))

        return keys
