from flask import Flask, request, render_template
from flask.wrappers import Response
from markupsafe import escape
import json
import secrets
from lib.viewModel import ViewModel

app = Flask(__name__)

ERROR_404 = { "code": 404 }

@app.route("/", methods=["GET"])
def index():
    return front("index")

@app.route("/<path:path>", methods=["GET"])
def front(path):
    """
    Display the html template at path.
    """
    try:
        r = render_template(path+".html")
        return r
    except:
        return "", 404

@app.route("/new", methods=["POST"])
def createNew():
    """
    Generate a new random token, and display a informational page.
    """
    token = secrets.token_urlsafe(16)
    model = ViewModel(token)
    model.update({}, "")
    return render_template("new.html", url=request.base_url[:-1*len(request.path)], token=token)

@app.route("/v1/<token>", methods=["GET"])
def getFull(token):
    return get("", token) 

@app.route("/v1/<token>/<path:path>", methods=["GET"])
def get(path, token):
    """
    Get an object, or set of objects.
    """
    model = ViewModel(token)
    try:
        data = model.read(path)
        return json.dumps(data)
    except Exception:
        return ERROR_404, 404


@app.route("/v1/<token>/<path:path>", methods=["POST"])
def post(path, token):
    """
    Create a new object.
    """
    model = ViewModel(token)
    return model.create(request.json, path), 201


@app.route("/v1/<token>/<path:path>", methods=["PUT"])
def put(path, token):
    """
    fully update an object.
    """
    model = ViewModel(token)
    try:
        return model.update(request.json, path), 200
    except Exception:
        return ERROR_404, 404

@app.route("/v1/<token>/<path:path>", methods=["PATCH"])
def patch(path, token):
    """
    Partially update an object
    """
    model = ViewModel(token)
    try:
        elem = model.read(path)
        if request.json != None:
            for k in request.json:
                elem[k] = request.json[k]
        return model.update(elem, path), 200
    except Exception:
        return ERROR_404, 404

@app.route("/v1/<token>/<path:path>", methods=["DELETE"])
def delete(path, token):
    model = ViewModel(token)
    try:
        model.delete(path)
        return "", 200
    except Exception:
        return ERROR_404, 404

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
