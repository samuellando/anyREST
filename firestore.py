from flask import request, abort
import json
import secrets
from firebase_admin import firestore
from anyrestHandlers import AnyrestHandlers

import os
os.environ['GRPC_DNS_RESOLVER'] = 'native'

class AnyrestHandlersFirestore(AnyrestHandlers):
    def __init__(self, db):
        self.db = db

    def anyrest_insert(self, path, data):
        if data is None:
            data = json.loads(request.data)
        if len(path.split("/")) % 2 == 0:
            ref = self.db.collection(path[:path.rindex("/")])
            ref = ref.document(path[path.rindex("/")+1:])
        else:
            ref = self.db.collection(path)
        return self.insert_data_into_firestore(data, ref)

    def insert_data_into_firestore(self, data, ref, merge=False):
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
                self.insert_data_into_firestore(d, ref.collection(collection))

        data = ref.get().to_dict()
        data["id"] = ref.id
        return data

    def anyrest_get(self, path, recursive):
        if recursive == None:
            recursive = True

        if len(path.split("/")) % 2 == 0:
            ref = self.db.collection(path[:path.rindex("/")])
            ref = ref.document(path[path.rindex("/")+1:])
        else:
            ref = self.db.collection(path)

        return self.get_data_from_firestore(ref, recursive)

    def anyrest_query(self, path, queries):
        if len(path.split("/")) % 2 == 0:
            abort(404)
        else:
            ref = self.db.collection(path)

        for q in queries:
            ref = ref.where(*q)

        data = []
        for doc in ref.stream():
            data.append(self.get_data_from_firestore(doc.reference, False, doc.to_dict()))

        return data

    def get_data_from_firestore(self, ref, recursive=True, data=None):
        if isinstance(ref, firestore.CollectionReference):
            data = []
            for doc in ref.stream():
                data.append(self.get_data_from_firestore(doc.reference, recursive, doc.to_dict()))
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
                    data[collection.id] = self.get_data_from_firestore(collection)

            return data
        else:
            raise Exception("ref must be a firestore.CollectionReference or a firestore.DocumentReference")


    def anyrest_patch(self, path, data):
        if data is None:
            data = json.loads(request.data)
        doc_ref = self.db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
        if doc_ref.get().exists:
            return self.insert_data_into_firestore(data, doc_ref, merge=True)
        else:
            abort(404)

    def anyrest_put(self, path, data):
        if data is None:
            data = json.loads(request.data)
        doc_ref = self.db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
        # If document exists.
        if doc_ref.get().exists:
            self.db.recursive_delete(doc_ref)
            return self.insert_data_into_firestore(data, doc_ref)
        else:
            abort(404)

    def anyrest_delete(self, path, data):
        doc_ref = self.db.collection(path[:path.rindex("/")]).document(path[path.rindex("/")+1:])
        # If document exists.
        if doc_ref.get().exists:
            self.db.recursive_delete(doc_ref)
            return "200"
        else:
            abort(404)

    def getApiKey(self, require_ath):
        with require_ath.acquire() as token:
            user = token.sub
            api_keys = self.db.collection("api-keys")
            query = api_keys.where("user", "==", user).stream()
            for key in query:
                return {"api-key": key.id}
            # Otherwise create a unique key for the user.
            api_key = secrets.token_urlsafe(64)
            while api_keys.document(api_key).get().exists:
                api_key = secrets.token_urlsafe(64)
            api_keys.document(api_key).set({"user": user})
            return {"api-key": api_key}

    def deleteApiKey(self, require_ath):
        with require_ath.acquire() as token:
            user = token.sub
            api_keys = self.db.collection("api-keys")
            query = api_keys.where("user", "==", user).stream()
            for key in query:
                key.reference.delete()
            return "200"

    def getUserFromApiKey(self, key):
        doc = self.db.collection("api-keys").document(key).get()
        if doc.exists:
            return {"user": doc.to_dict()["user"]}
        abort(403)
