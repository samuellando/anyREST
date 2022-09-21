from flask import Flask
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
        print(data)
        if k in data:
            data = data[k]
        else:
            return None
    
    return data

@app.route("/<path:path>", methods=["GET"])
def get(path):
    layers = path.split("/")

    data = loadData()

    elem = getByKeys(data, layers)

    if elem == None:
        return "404", 404

    return elem

@app.route("/<path:path>", methods=["POST"])
def post(path):
    # TODO read request body for data.
    new = {"new": "data"}

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
        id = str(int(max(col.keys())) + 1)
    else:
        id = "0"

    col[id] = new 

    saveData(data)

    return str(id)

@app.route("/<path:path>", methods=["PUT"])
def put(path):
    # TODO read request body.
    update = {'what': 'txt'}

    layers = path.split("/")

    data = loadData()

    elem = getByKeys(data, layers)

    if elem == None:
        return "404", 404

    for key in update:
        elem[key] = update[key]

    saveData(data)

    return data

@app.route("/<path:path>", methods=["DELETE"])
def delete(path):
    layers = path.split("/")

    data = loadData()

    col = getByKeys(data,layers[:-1])

    if col == None:
        return "404", 404

    col[layers[-1]] = None

    saveData(data)

    return data

if __name__ == "__main__":
    saveData({})
    print(post("users/0/baselines/0/counters"))
    print(post("users/0/baselines/0/counters"))
    print(get("users/0/baselines/0/counters/0"))
    print(delete("users/0/baselines/0/counters/0"))
    print(put("users/0/baselines/0/counters/1"))
    print(delete("users/0/baselines/0/counters/1"))
    print(get("users/0/baselines/0/counters/1"))

