from flask import request, abort

from abc import ABC, abstractmethod
class AnyrestHandlers(ABC):
    @abstractmethod
    def anyrest_insert(self, path, data):
        return {}

    @abstractmethod
    def anyrest_get(self, path, recursive):
        return {}

    @abstractmethod
    def anyrest_query(self, path, queries):
        return {}

    @abstractmethod
    def anyrest_patch(self, path, data):
        return {}

    @abstractmethod
    def anyrest_put(self, path, data):
        return {}

    @abstractmethod
    def anyrest_delete(self, path, noting):
        return {}

    @abstractmethod
    def getApiKey(self, require_ath, db):
        with require_ath.acquire() as token:
            user = token.sub
            return {"api-key": ""}

    @abstractmethod
    def deleteApiKey(self, require_ath, db):
        with require_ath.acquire() as token:
            user = token.sub
            return 200 


    def protect(self, require_auth, path, fn, data):
        user = None
        try:
            with require_auth.acquire() as token:
                user = token.sub
        except:
            if "api-key" in request.headers:
                key = request.headers["api-key"]
                user = self.anyrest_get("api-keys/"+key, None)["user"]

        if user is None:
            abort(401)
        else:
            return fn("users/{}/{}".format(user, path), data)
