from flask import Blueprint, request, render_template
import json
import secrets
from .viewModel import ViewModel
from .utils import sort, filter, fields as utils_fields

api = Blueprint("anyrest api", __name__, template_folder="templates")

ERROR_404 = { "code": 404 }

@api.route("/", methods=["GET"])
def index():
    return front("index")

@api.route("/<path:path>", methods=["GET"])
def front(path):
    """
    Display the html template at path.
    """
    try:
        r = render_template(path+".html")
        return r
    except:
        return "", 404

@api.route("/new", methods=["POST"])
def createNew():
    """
    Generate a new random token, and display a informational page.
    """
    while True:
        try:
            token = secrets.token_urlsafe(16)
            model = ViewModel(token)
            model.read("")
        except:
            break
    return render_template("new.html", url=request.base_url[:-1*len(request.path)], token=token)

@api.route("/v1/<token>", methods=["GET"])
def getFull(token):
    return get("", token) 

@api.route("/v1/<token>/<path:path>", methods=["GET"])
def get(path, token):
    """
    Get an object, or set of objects.
    """
    model = ViewModel(token)
    try:
        data = model.read(path)
        # Because it might be a list.
        return json.dumps(data)
    except Exception:
        return ERROR_404, 404


@api.route("/v1/<token>/<path:path>", methods=["POST"])
def post(path, token):
    """
    Create a new object.
    """
    model = ViewModel(token)
    return model.create(request.json, path), 201


@api.route("/v1/<token>/<path:path>", methods=["PUT"])
def put(path, token):
    """
    fully update an object.
    """
    model = ViewModel(token)
    return model.update(request.json, path), 200

@api.route("/v1/<token>/<path:path>", methods=["PATCH"])
def patch(path, token):
    """
    Partially update an object
    """
    model = ViewModel(token)
    return model.partialUpdate(request.json, path), 200

@api.route("/v1/<token>/<path:path>", methods=["DELETE"])
def delete(path, token):
    model = ViewModel(token)
    model.delete(path)
    return "", 200

@api.after_request
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
    data = filter(data, filters)

    # Sorting.
    sorts = request.args.get('sort')
    if sorts != None:
        sorts = sorts.split(",")
        data = sort(data, sorts)

    # Only include certain feilds in the output.
    fields = request.args.get('fields')
    if fields != None:
        fields = fields.split(",")
        data = utils_fields(data, fields)

    # Pretty print the json.
    pretty = request.args.get('pretty')
    if pretty == "true":
        response.set_data(json.dumps(data, indent=2))
    else:
        response.set_data(json.dumps(data))

    return response

