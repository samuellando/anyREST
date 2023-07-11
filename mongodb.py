from anyrestHandlers import AnyrestHandlers
from flask import abort, request
import json
from bson.objectid import ObjectId

class AnyrestHandlersMongoDB(AnyrestHandlers):
    def __init__(self, db):
        self.db = db

    def decunstructPath(self, path):
        l = path.split("/")
        if len(l) % 2 == 0:
            id = l[-1]
            col = l[-2]
            path = "/".join(l[:-2])
        else:
            id = None
            col = l[-1]
            path = "/".join(l[:-1])

        return path, col,  id

    def resToDict(self, d, res= None):
        if res != None:
            d["id"] = str(res.inserted_id)
        else:
            d["id"] = str(d["_id"])
        del d["_id"]
        del d["anyrest_path"]
        return d

    def toObjectId(self,id):
        try:
            return ObjectId(id)
        except:
            return id

    def anyrest_insert(self, path, data):
        path, col, id = self.decunstructPath(path)
        if data is None:
            data = json.loads(request.data)
        else:
            data = data.copy()
        if id != None:
            data["_id"] = id
        col = self.db[col]
        data["anyrest_path"] = path
        res = col.insert_one(data)
        return self.resToDict(data, res)

    def anyrest_get(self, path, nothing):
        path, col, id = self.decunstructPath(path)
        col = self.db[col]
        if id == None:
            return list(map(self.resToDict, col.find({"anyrest_path": path})))
        else:
            res = col.find_one({"anyrest_path": path, "_id": self.toObjectId(id)})
            if res == None:
                abort(404)
            else:
                return self.resToDict(res)

    def anyrest_query(self, path, a):
        path, col, id = self.decunstructPath(path)
        col = self.db[col]
        if id != None:
            abort(400)

        res = col.find({ "$and": [{"anyrest_path": path}, a[0]]})
        if len(a) > 1 and a[1] != None:
            res = res.sort(*list(a[1].items())[0])
        if len(a) > 2:
            res = res.limit(a[2])

        return list(map(self.resToDict, res))

    def anyrest_patch(self, path, data):
        path, col, id = self.decunstructPath(path)
        if id == None:
            abort(400)
        if data is None:
            data = json.loads(request.data)
        else:
            data = data.copy()
        col = self.db[col]
        res = col.update_one({"anyrest_path": path, "_id": self.toObjectId(id)}, {"$set": data})
        if res.matched_count == 0:
            abort(404)
        res = col.find_one({"anyrest_path": path, "_id": self.toObjectId(id)})
        return self.resToDict(res)

    def anyrest_put(self, path, data):
        path, col, id = self.decunstructPath(path)
        if id == None:
            abort(400)
        if data is None:
            data = json.loads(request.data)
        else:
            data = data.copy()
        col = self.db[col]
        data["anyrest_path"] = path
        res = col.replace_one({"anyrest_path": path, "_id": self.toObjectId(id)}, data)
        if res.matched_count == 0:
            abort(404)
        res = col.find_one({"anyrest_path": path, "_id": self.toObjectId(id)})
        return self.resToDict(res)

    def anyrest_delete(self, path, noting):
        path, col, id = self.decunstructPath(path)
        if id == None:
            abort(400)
        col = self.db[col]
        res = col.delete_one({"anyrest_path": path, "_id": self.toObjectId(id)})
        if res.deleted_count == 0:
            abort(404)
        else:
            return "200"

    def getApiKey(self, require_ath):
        with require_ath.acquire() as token:
            user = token.sub
            col = self.db["api-keys"]
            res = col.find_one({"user": user})
            if res is None:
                abort(404)
            else:
                return {"api-key": res["api-key"]}

    def deleteApiKey(self, require_ath):
        with require_ath.acquire() as token:
            user = token.sub
            col = self.db["api-keys"]
            col.delete_one({"user": user})
            return 200 

    def getUserFromApiKey(self, key):
        col = self.db["api-keys"]
        res = col.find_one({"api-key": key})
        if res is None:
            abort(403)
        else:
            return {"user": res["user"]}

