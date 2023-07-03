class Handlers:
    def __init__(self, get, post, patch, put, delete, query, getApiKey, deleteApiKey):
        self.get = get
        self.post = post
        self.patch = patch
        self.put = put
        self.delete = delete
        self.query = query
        self.getApiKey = getApiKey
        self.deleteApiKey = deleteApiKey

class TestingHandlers(Handlers):
    def __init__(self, handlers, clear):
        self.get = handlers.get
        self.post = handlers.post
        self.patch = handlers.patch
        self.put = handlers.put
        self.delete = handlers.delete
        self.query = handlers.query
        self.getApiKey = handlers.getApiKey
        self.deleteApiKey = handlers.deleteApiKey
        self.clear = clear


def addAnyrestHandlers(app, db, authority, audience, lock):
    if authority is not None:
        from authlib.integrations.flask_oauth2 import ResourceProtector
        from validator import Auth0JWTBearerTokenValidator
        require_auth = ResourceProtector()
        validator = Auth0JWTBearerTokenValidator(
            authority,
            audience
        )
        require_auth.register_token_validator(validator)
    else:
        validator = None
        require_auth = None

    def wrap(fn):
        if validator is None:
            return lambda path, data=None: fn(path, data)
        else:
            return lambda path, data=None: db.protect(require_auth, path, fn, data)

    funcs = Handlers(wrap(db.anyrest_get), wrap(db.anyrest_insert), wrap(db.anyrest_patch), wrap(db.anyrest_put), wrap(db.anyrest_delete), wrap(db.anyrest_query), wrap(db.getApiKey), wrap(db.deleteApiKey))

    if not lock:
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_post_path", view_func=funcs.post, methods=["POST"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_get_path", view_func=funcs.get, methods=["GET"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_patch_path", view_func=funcs.patch, methods=["PATCH"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_put_path", view_func=funcs.put, methods=["PUT"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_delete_path", view_func=funcs.delete, methods=["DELETE"])
        app.add_url_rule('/api/<path:path>', endpoint="anyrest_query_path", view_func=funcs.query, methods=["GET"])
        if validator is not None: 
            app.add_url_rule('/api-key', endpoint="anyrest_get_api_key", view_func=lambda : funcs.getApiKey(require_auth, db), methods=["GET"])
            app.add_url_rule('/api-key', endpoint="anyrest_delete_api_key", view_func=lambda : funcs.deleteApiKey(require_auth, db), methods=["DELETE"])

    return funcs

def addAnyrestHandlersMongoDB(app, db, authority=None, audience=None, lock=False):
    from mongodb import AnyrestHandlersMongoDB
    db = AnyrestHandlersMongoDB(db)
    return addAnyrestHandlers(app, db, authority, audience, lock)

def addAnyrestHandlersFireStore(app, db, authority=None, audience=None, lock=False):
    from firestore import AnyrestHandlersFirestore
    db = AnyrestHandlersFirestore(db)
    return addAnyrestHandlers(app, db, authority, audience, lock)

def addAnyrestHandlersTesting(app, authority=None, audience=None, lock=False):
    from testing import AnyrestHandlersTesting
    db = AnyrestHandlersTesting()
    ar = addAnyrestHandlers(app, db, authority, audience, lock)
    ar = TestingHandlers(ar, db.clear)
    return ar

if __name__ == "__main__":
    from flask import Flask
    from flask_cors import CORS

    app = Flask(__name__)

    addAnyrestHandlersTesting(app)

    CORS(app)
    app.run(host='127.0.0.1', port=8080, debug=True)
