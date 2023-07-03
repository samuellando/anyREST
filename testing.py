from mongodb import AnyrestHandlersMongoDB
import mongomock

class AnyrestHandlersTesting(AnyrestHandlersMongoDB):
    def __init__(self):
        super(AnyrestHandlersTesting, self).__init__(mongomock.MongoClient().db)

    def clear(self):
        self.db = mongomock.MongoClient().db


