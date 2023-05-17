from flask import Flask, request
import json
import secrets
import firebase_admin
from firebase_admin import firestore

import os
os.environ['GRPC_DNS_RESOLVER'] = 'native'

def anyrest_insert(db, path, data):
    if data is None:
        data = json.loads(request.data)
    return insert_data_into_firestore(data, db.collection(path))

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

    return {"id": ref.id, "data": ref.get().to_dict()}

def anyrest_get(db, path, data):
    if len(path.split("/")) % 2 == 0:
        ref = db.collection(path[:path.rindex("/")])
        ref = ref.document(path[path.rindex("/")+1:])
    else:
        ref = db.collection(path)

    return get_data_from_firestore(ref)

def get_data_from_firestore(ref):
    if isinstance(ref, firestore.CollectionReference):

        data = {}
        for doc in ref.stream():
            data[doc.id] = get_data_from_firestore(doc.reference)
        return data
    elif isinstance(ref, firestore.DocumentReference):
        data = ref.get().to_dict()
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
    return insert_data_into_firestore(data, doc_ref, merge=True)

def anyrest_put(db, path, data):
    if data is None:
        data = json.loads(request.data)
    doc_ref = db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
    # If document exists.
    if doc_ref.get().exists:
        db.recursive_delete(doc_ref)
        return insert_data_into_firestore(data, doc_ref)
    else:
        return {"code": 404}

def anyrest_delete(db,path, data):
    doc_ref = db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
    # If document exists.
    if doc_ref.get().exists:
        db.recursive_delete(doc_ref)
        return {"code": 200}
    else:
        return {"code": 404}

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
        return {"code": 200}


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
        return {"message": 401}, 401
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

    funcs = {
            "GET":wrap(anyrest_get),
            "POST":wrap(anyrest_insert),
            "PATCH":wrap(anyrest_patch),
            "PUT":wrap(anyrest_put),
            "DELETE":wrap(anyrest_delete)
            }

    if not lock:
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_post_path", view_func=funcs["POST"], methods=["POST"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_get_path", view_func=funcs["GET"], methods=["GET"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_patch_path", view_func=funcs["PATCH"], methods=["PATCH"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_put_path", view_func=funcs["PUT"], methods=["PUT"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_delete_path", view_func=funcs["DELETE"], methods=["DELETE"])

    return funcs

if __name__ == '__main__':
    firebase_app = firebase_admin.initialize_app()
    db = firestore.client()

    app = Flask(__name__)
    from flask_cors import CORS
    CORS(app)
    addAnyrestHandlers(app, db)
    app.run(host='127.0.0.1', port=8080, debug=True)
