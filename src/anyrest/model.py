import time
from .firestore_odr import FirestoreOdr
from typing import Optional, Any
from .abstract_odr import AbstractOdr, dict


class Model:
    def __init__(self, token: str, odr: Optional[AbstractOdr] = None):
        self.token = token
        if odr is None:
            self.odr = FirestoreOdr()
        else:
            self.odr = odr

    def __updateMeta(self, data: dict) -> None:
        """
        Writes the metadata for a specific token.
        """
        self.odr.update(f'meta/{self.token}', data)

    def read(self, path: str) -> dict:
        return self.odr.get(f'tokens/{self.token}/{path}')

    def __updateLastModified(self) -> None:
        """
        Updates the last modfified metadata for the token.
        """
        meta = {"lastModified": time.time_ns()}
        self.__updateMeta(meta)

    def insert(self, e: dict, path: str) -> dict:
        """
        Inserts e at layers, giving it the next numeric id.
        """
        def _safeInt(i: Any) -> int:
            # If an id is not convertable to int, make it -1
            try:
                return int(i)
            except ValueError:
                return -1

        try:
            p = self.odr.get(f'tokens/{self.token}/{path}')
        except KeyError:
            p = {}

        if len(p.keys()) > 0:
            # if the max is -1, id will be 0.
            id = max(map(lambda x: _safeInt(x), p.keys())) + 1
        else:
            id = 0

        e["id"] = id

        self.__updateLastModified()
        self.odr.set(f'tokens/{self.token}/{path}/{id}', e)
        return e

    def write(self, e: dict, path: str = "") -> dict:
        """
        writes the object to data[...keys], updates lastmodified metadata.
        """
        self.__updateLastModified()
        self.odr.set(f'tokens/{self.token}/{path}', e)
        return e

    def update(self, e: dict, path: str = "") -> dict:
        """
        updates the object to data[...keys], updates lastmodified metadata.
        """
        self.__updateLastModified()
        e = self.odr.update(f'tokens/{self.token}/{path}', e)
        return e

    def remove(self, path: str) -> None:
        """
        Removes data[...layers], throws not found.
        """
        self.odr.delete(f'tokens/{self.token}/{path}')
