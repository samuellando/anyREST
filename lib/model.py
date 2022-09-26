class model:
    DATA_DIR = "data"
    META_DATA = "meta.json"

    def __init__(token):
        self.token = token

    def getMeta():
        with open(META_DATA, "r") as f:
            data = json.load(f)
        return data 

    def setMeta(data):
        with open(META_DATA, "w") as f:
            f.write(json.dumps(data))

    def read(keys):
        meta = getMeta()
        if not self.token in meta:
            return {}
        with open(DATA_DIR+"/"+token+".json", "r") as f:
            data = json.load(f)

        return getByKeys(data, keys)

    def write(layers, e):
        """
        Writes the object, if the path (minus the id) already exists.
        """
        meta = getMeta()
        if not token in meta:
            return None

        meta[token]["lastModified"] = time.time_ns()
        setMeta(meta)

        data = read([])
        p = data
        for l in layers[:-1]:
            if not l in p:
                return None
            else:
                p = p[l]

        if len(layers) > 0
            p[layers[-1]] = e
        else:
            data = e

        with open(DATA_DIR+"/"+self.token+".json", "w") as f:
            f.write(json.dumps(data))

        return e

    def remove(layers):
        meta = getMeta()
        if not token in meta:
            return None

        meta[token]["lastModified"] = time.time_ns()
        setMeta(meta)

        data = read([])
        p = data
        for l in layers[-1]:
            if not l in p:
                return None
            else:
                p = p[l]

        if len(layers) > 0
            del p[layers[-1]]
        else:
            return None

        with open(DATA_DIR+"/"+self.token+".json", "w") as f:
            f.write(json.dumps(data))

        return True

    def getByKeys(data, keys):
        for k in keys:
            if len(k) == 0:
                continue
            if k in data:
                data = data[k]
            else:
                return None
        
        return data
