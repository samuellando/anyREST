from .model import Model

class ViewModel:
    DATA_DIR = "data"
    def __init__(self, token, dataDir=DATA_DIR):
        self.token = token
        self.model = Model(token, dataDir)

    def create(self, e, path):
        layers = path.split("/")
        return self.model.insert(e, layers)

    def read(self, path):
        layers = path.split("/")
        data = self.model.read(layers)
        # If all elements in data have an int id, convert to a list.
        isList = True 
        for k in data.keys():
            try:
                int(k)
            except ValueError:
                isList = False

        if isList:
            return list(data.values())
        else:
            return data

    def update(self, e, path):
        layers = path.split("/")
        return self.model.write(e, layers)

    def delete(self, path):
        layers = path.split("/")
        print(layers)
        return self.model.remove(layers)
