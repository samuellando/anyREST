class viewModel:
    def __init__(token):
        self.token = token
        self.model = Model(token)

    def create(self, path, e):
        layers = path.split("/")
        data = self.model.read([])

        parents = {}
        for l in reversed(layers):
            parents = {l: parents}


        {}

        tests/0/cols

        p = {tests: {0: cols: {}}}

        p = data
        insertLayers = []
        for l in layers:
            if l in p:
                parents = parents[l]
                p = p[l]
                insertLayers.append(l)
            else:
                p[l] = parents[l]
                break

        p2 = p
        while len(p2.keys()) > 0:
            p2 = p2[p2.keys()[0]]

        if len(p2.keys()) > 0:
            try:
                id = str(max(map(lambda x:int(x), p2.keys())) + 1)
            except ValueError:
                return None
        else:
            id = "0"

        e["id"] = int(id)
        p2[id] = e

        return self.model.write(insertLayers, p)

    def read(self, path, obj):
        layers = path.split("/")
        return self.model.read(layers)

    def update(self, path, obj):
        layers = path.split("/")
        return self.model.write(layers, obj)

    def delete(self, path, obj):
        layers = path.split("/")
        return self.model.remove(layers)
