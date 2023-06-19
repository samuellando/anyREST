from flask import Flask, request, abort
import json
import secrets
import firebase_admin
from firebase_admin import firestore

import os
os.environ['GRPC_DNS_RESOLVER'] = 'native'

def anyrest_insert(db, path, data):
    if data is None:
        data = json.loads(request.data)
    if len(path.split("/")) % 2 == 0:
        ref = db.collection(path[:path.rindex("/")])
        ref = ref.document(path[path.rindex("/")+1:])
    else:
        ref = db.collection(path)
    return insert_data_into_firestore(data, ref)

def insert_data_into_firestore(data, ref, merge=False):
    # Make sure the parameters are valid, throw.
    if not isinstance(data, dict):
        raise Exception("data must be a dictionary")
    if not isinstance(ref, firestore.CollectionReference) and not isinstance(ref, firestore.DocumentReference):
        raise Exception("col_ref must be a firestore Reference")

    collections = {}
    values = {}
    for key, value in data.items():
        if isinstance(value, list):
            collections[key] = value
        else:
            values[key] = value
    if isinstance(ref, firestore.CollectionReference):
        ref = ref.document()
    ref.set(values, merge=merge)
    for collection, l in collections.items():
        for d in l:
            insert_data_into_firestore(d, ref.collection(collection))

    data = ref.get().to_dict()
    data["id"] = ref.id
    return data

def anyrest_get(db, path, recursive):
    if recursive == None:
        recursive = True

    if len(path.split("/")) % 2 == 0:
        ref = db.collection(path[:path.rindex("/")])
        ref = ref.document(path[path.rindex("/")+1:])
    else:
        ref = db.collection(path)

    return get_data_from_firestore(ref, recursive)


def get_data_from_firestore(ref, recursive=True, data=None):
    if isinstance(ref, firestore.CollectionReference):
        data = []
        for doc in ref.stream():
            data.append(get_data_from_firestore(doc.reference, recursive, doc.to_dict()))
        return data
    elif isinstance(ref, firestore.DocumentReference):
        if data == None:
            data = ref.get()
            if not data.exists:
                abort(404)
            data = data.to_dict()
        data["id"] = ref.id
        if recursive:
            collections = ref.collections()
            for collection in collections:
                data[collection.id] = get_data_from_firestore(collection)

        return data
    else:
        raise Exception("ref must be a firestore.CollectionReference or a firestore.DocumentReference")


def anyrest_patch(db, path, data):
    if data is None:
        data = json.loads(request.data)
    doc_ref = db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
    if doc_ref.get().exists:
        return insert_data_into_firestore(data, doc_ref, merge=True)
    else:
        abort(404)

def anyrest_put(db, path, data):
    if data is None:
        data = json.loads(request.data)
    doc_ref = db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
    # If document exists.
    if doc_ref.get().exists:
        db.recursive_delete(doc_ref)
        return insert_data_into_firestore(data, doc_ref)
    else:
        abort(404)

def anyrest_delete(db,path, data):
    doc_ref = db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
    # If document exists.
    if doc_ref.get().exists:
        db.recursive_delete(doc_ref)
        return 200
    else:
        abort(404)

def get_api_key(require_ath, db):
    with require_ath.acquire() as token:
        user = token.sub
        api_keys = db.collection("api-keys")
        query = api_keys.where("user", "==", user).stream()
        for key in query:
            return {"api-key": key.id}
        # Otherwise create a unique key for the user.
        api_key = secrets.token_urlsafe(64)
        while api_keys.document(api_key).get().exists:
            api_key = secrets.token_urlsafe(64)
        api_keys.document(api_key).set({"user": user})
        return {"api-key": api_key}

def delete_api_key(require_ath, db):
    with require_ath.acquire() as token:
        user = token.sub
        api_keys = db.collection("api-keys")
        query = api_keys.where("user", "==", user).stream()
        for key in query:
            key.reference.delete()
        abort(200)


def protect(require_auth, db, path, fn, data):
    user = None
    try:
        with require_auth.acquire() as token:
            user = token.sub
    except:
        if "api-key" in request.headers:
            key = request.headers["api-key"]
            user = anyrest_get(db, "api-keys/"+key, None)["user"]

    if user is None:
        abort(401)
    else:
        return fn(db, "users/{}/{}".format(user, path), data)

def addAnyrestHandlers(app, db, authority=None, audience=None, lock=False):
    if authority is not None:
        from authlib.integrations.flask_oauth2 import ResourceProtector
        from validator import Auth0JWTBearerTokenValidator
        require_auth = ResourceProtector()
        validator = Auth0JWTBearerTokenValidator(
            authority,
            audience
        )
        require_auth.register_token_validator(validator)
        app.add_url_rule('/api-key', endpoint="anyrest_get_api_key", view_func=lambda : get_api_key(require_auth, db), methods=["GET"])
        app.add_url_rule('/api-key', endpoint="anyrest_delete_api_key", view_func=lambda : delete_api_key(require_auth, db), methods=["DELETE"])
    else:
        validator = None

    def wrap(fn):
        if validator is None:
            return lambda path, data=None: fn(db, path, data)
        else:
            return lambda path, data=None: protect(require_auth, db, path, fn, data)

    funcs = Handlers(wrap(anyrest_get), wrap(anyrest_insert), wrap(anyrest_patch), wrap(anyrest_put), wrap(anyrest_delete))

    if not lock:
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_post_path", view_func=funcs.post, methods=["POST"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_get_path", view_func=funcs.get, methods=["GET"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_patch_path", view_func=funcs.patch, methods=["PATCH"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_put_path", view_func=funcs.put, methods=["PUT"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_delete_path", view_func=funcs.delete, methods=["DELETE"])

    return funcs

if __name__ == '__main__':
    firebase_app = firebase_admin.initialize_app()
    db = firestore.client()

    app = Flask(__name__)
    from flask_cors import CORS
    CORS(app)
    addAnyrestHandlers(app, db)
    app.run(host='127.0.0.1', port=8080, debug=True)

class Handlers:
    def __init__(self, get, post, patch, put, delete):
        self.get = get
        self.post = post
        self.patch = patch
        self.put = put
        self.delete = delete
