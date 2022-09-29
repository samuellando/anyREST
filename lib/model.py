import time
import json

class Model:
    META_DATA = "meta.json"

    def __init__(self, token, dataDir):
        self.dataDir = dataDir
        self.token = token

    def __getAllMeta(self):
        """
        Returns all the metadata for all tokens in dict format.
        """
        try:
            with open(f'{self.dataDir}/{Model.META_DATA}', "r") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            return {}

    def __getMeta(self):
        """
        Gets the metadata on a token.
        returns empty dict if no metadata exists.
        """
        data = self.__getAllMeta()
        return data[self.token] if self.token in data else {} 

    def __setMeta(self, data):
        """
        Writes the metadata for a specific token.
        """
        meta = self.__getMeta()
        meta[self.token] = data
        with open(Model.META_DATA, "w") as f:
            f.write(json.dumps(meta))

    def __getByKeys(self, data, keys):
        """
        Gets data[...keys]
        """
        for k in keys:
            if len(k) == 0:
                continue
            if k in data:
                data = data[k]
            else:
                raise Exception("Not found")
        
        return data

    def read(self, keys=[]):
        """
        Tries to get  data[...keys] for the token, and returns None if it is not found.
        """
        try:
            with open(self.dataDir+"/"+self.token+".json", "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise Exception("Not Found")

        return self.__getByKeys(data, keys)

    def __updateLastModified(self):
        """
        Updates the last modfified metadata for the token.
        """
        meta = {"lastModified": time.time_ns()}
        self.__setMeta(meta)

    def __addMissingLayers(self, layers, data):
        """
        Adds the layers if they are missing in the dict. 
        """ 
        # Create a dict with all layers.
        parents = {}
        for l in reversed(layers):
            parents = {l: parents}

        # "Append" this missing layers.
        p = data
        for l in layers:
            if l in p:
                parents = parents[l]
                p = p[l]
            else:
                p[l] = parents[l]
                break

        return data

    def insert(self, e, layers):
        """
        Inserts e at layers, giving it the next numeric id.
        """
        try:
            data = self.read()
        except Exception:
            data = {}

        data = self.__addMissingLayers(layers, data)

        p = data
        for l in layers:
            p = p[l]

        def safeInt(i):
            # If an id is not convertable to int, make it -1
            try:
                return int(i)
            except ValueError:
                return -1

        if len(p.keys()) > 0:
            # if the max is -1, id will be 0.
            id = max(map(lambda x:safeInt(x), p.keys())) + 1
        else:
            id = 0

        e["id"] = id
        p[str(id)] = e

        self.write(data)
        return e

    def write(self, e, layers=[]):
        """
        Writes the object to data[...keys], updates lastModified metadata.
        raises exception if layers do not exists.
        """
        # Pull all data.
        try:
            data = self.read()
        except: # Not found
            data = {}
        # Check if the layers are in data.
        p = data
        for l in layers[:-1]:
            if not l in p:
                raise Exception("Not found")
            else:
                p = p[l]

        if len(layers) > 0:
            # Insert e.
            p[layers[-1]] = e
        else:
            # If no layers were provided.
            data = e

        with open(f'{self.dataDir}/{self.token}.json', "w") as f:
            f.write(json.dumps(data))

        self.__updateLastModified()
        return e

    def remove(self, layers):
        """
        Removes data[...layers], throws not found.
        """
        data = self.read([])
        
        p = data
        for l in layers[:-1]:
            if not l in p:
                raise Exception("Not found")
            else:
                p = p[l]

        if len(layers) > 0:
            del p[layers[-1]]
        else:
            data = {}

        self.write(data)
        return True

