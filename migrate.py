from pymongo import MongoClient
from pymongo.server_api import ServerApi
import firebase_admin
from firebase_admin import firestore

import os
os.environ['GRPC_DNS_RESOLVER'] = 'native'

firebase_app = firebase_admin.initialize_app(options={'projectId': 'timelogger-slando'})
fb = firestore.client()

uri = "mongodb+srv://{}:{}@hackline.1ofbp0v.mongodb.net/?retryWrites=true&w=majority".format(os.environ["MONGODB_USER"], os.environ["MONGODB_PASSWORD"])
client = MongoClient(uri,
                     tls=True,
                     server_api=ServerApi('1'))
mdb = client['production']

def migrateAll(ref, path):
    for col in ref.collections(): 
        print(path, col.id)

        for doc in col.stream():
            data = doc.to_dict()
            print(path, col.id, doc.id)
            data["anyrest_path"] = path
            mdb[col.id].insert_one(data)

        for doc in col.list_documents():
            migrateAll(doc, path+"/" +col.id+"/"+doc.id if path != "" else col.id+"/"+doc.id)

if __name__ == "__main__":
    migrateAll(fb, "")
