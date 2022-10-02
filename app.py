from flask import Flask, request, render_template
from flask.wrappers import Response
from markupsafe import escape
import json
import secrets
from lib.viewModel import ViewModel
import lib.utils as utils

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


    # Filtering.
    exclude = ['pretty', 'fields','sort']
    filters  = {}
    for f in request.args:
        # Exclude the other params
        if not f in exclude:
            filters[f] = request.args[f]
    data = utils.filter(data, filters)

    # Sorting.
    sorts = request.args.get('sort')
    if sorts != None:
        sorts = sorts.split(",")
        data = utils.sort(data, sorts)

    # Only include certain feilds in the output.
    fields = request.args.get('fields')
    if fields != None:
        fields = fields.split(",")
        data = utils.fields(data, fields)

    # Pretty print the json.
    pretty = request.args.get('pretty')
    if pretty == "true":
        response.set_data(json.dumps(data, indent=2))
    else:
        response.set_data(json.dumps(data))

    return response

