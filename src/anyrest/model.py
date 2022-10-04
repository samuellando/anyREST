import time
import json
from .firestore_odr import Odr

class Model:
    def __init__(self, token):
        self.token = token
        self.odr = Odr()

    def __getMeta(self):
        """
        Gets the metadata on a token.
        returns empty dict if no metadata exists.
        """
        try:
            return self.odr.get(f'meta/{self.token}')
        except Exception:
            return {}

    def __updateMeta(self, data):
        """
        Writes the metadata for a specific token.
        """
        self.odr.update(f'meta/{self.token}', data)

    def read(self, path):
        """
        Tries to get  data[...keys] for the token, and returns None if it is not found.
        """
        return self.odr.get(f'tokens/{self.token}/{path}')

    def __updateLastModified(self):
        """
        Updates the last modfified metadata for the token.
        """
        meta = {"lastModified": time.time_ns()}
        self.__updateMeta(meta)

    def insert(self, e, path):
        """
        Inserts e at layers, giving it the next numeric id.
        """
        def _safeInt(i):
            # If an id is not convertable to int, make it -1
            try:
                return int(i)
            except ValueError:
                return -1

        try:
            p = self.odr.get(f'tokens/{self.token}/{path}')
        except Exception:
            p = {}

        if len(p.keys()) > 0:
            # if the max is -1, id will be 0.
            id = max(map(lambda x:_safeInt(x), p.keys())) + 1
        else:
            id = 0

        e["id"] = id

        self.__updateLastModified()
        self.odr.set(f'tokens/{self.token}/{path}/{id}', e)
        return e

    def write(self, e, path=""):
        """
        writes the object to data[...keys], updates lastmodified metadata.
        """
        self.__updateLastModified()
        self.odr.set(f'tokens/{self.token}/{path}', e)
        return e

    def update(self, e, path):
        """
        updates the object to data[...keys], updates lastmodified metadata.
        """
        self.__updateLastModified()
        e = self.odr.update(f'tokens/{self.token}/{path}', e)
        return e
 
    def remove(self, path):
        """
        Removes data[...layers], throws not found.
        """
        self.odr.delete(f'tokens/{self.token}/{path}')
