from flask import Flask, request
import json
import firebase_admin
from firebase_admin import firestore

import os
os.environ['GRPC_DNS_RESOLVER'] = 'native'

def anyrest_insert(db, path):
    data = json.loads(request.data)
    return insert_data_into_firestore(data, db.collection(path))

def anyrest_insert_base(db):
    data = json.loads(request.data)
    return insert_data_into_firestore(data, db.collection("anyrest"))

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

def anyrest_get(db, path):
    if len(path.split("/")) % 2 == 0:
        ref = db.collection(path[:path.rindex("/")])
        ref = ref.document(path[path.rindex("/")+1:])
    else:
        ref = db.collection(path)

    return get_data_from_firestore(ref)

def anyrest_get_base(db):
    return get_data_from_firestore(db.collection("anyrest"))

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


def anyrest_patch(db, path):
    data = json.loads(request.data)
    doc_ref = db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
    return insert_data_into_firestore(data, doc_ref, merge=True)

def anyrest_put(db, path):
    data = json.loads(request.data)
    doc_ref = db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
    # If document exists.
    if doc_ref.get().exists:
        db.recursive_delete(doc_ref)
        return insert_data_into_firestore(data, doc_ref)
    else:
        return {"code": 404}

def anyrest_delete(db,path):
    doc_ref = db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
    # If document exists.
    if doc_ref.get().exists:
        db.recursive_delete(doc_ref)
        return {"code": 200}
    else:
        return {"code": 404}

def addAnyrestHandlers(app, db):
    app.add_url_rule('/api/<path:path>', endpoint="anyrest_post_path", view_func=lambda path : anyrest_insert(db, path), methods=["POST"])
    app.add_url_rule('/api', endpoint="anyrest_post", view_func=lambda : anyrest_insert_base(db), methods=["POST"])
    app.add_url_rule('/api/<path:path>', endpoint="anyrest_get_path", view_func=lambda path : anyrest_get(db, path), methods=["GET"])
    app.add_url_rule('/api', endpoint="anyrest_get", view_func=lambda : anyrest_get_base(db), methods=["GET"])
    app.add_url_rule('/api/<path:path>', endpoint="anyrest_patch_path", view_func=lambda path : anyrest_patch(db, path), methods=["PATCH"])
    app.add_url_rule('/api/<path:path>', endpoint="anyrest_put_path", view_func=lambda path : anyrest_put(db, path), methods=["PUT"])
    app.add_url_rule('/api/<path:path>', endpoint="anyrest_delete_path", view_func=lambda path : anyrest_delete(db, path), methods=["DELETE"])

if __name__ == '__main__':
    firebase_app = firebase_admin.initialize_app()
    db = firestore.client()

    app = Flask(__name__)
    from flask_cors import CORS
    addAnyrestHandlers(app, db)
    app.run(host='127.0.0.1', port=8080, debug=True)
