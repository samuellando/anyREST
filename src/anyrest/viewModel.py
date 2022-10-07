from .model import Model

class ViewModel:
    def __init__(self, token):
        self.token = token
        self.model = Model(token)

    def create(self, e, path):
        return self.model.insert(e, path)

    def read(self, path):
        data = self.model.read(path)
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
        return self.model.write(e, path)

    def partialUpdate(self, e, path):
        return self.model.update(e, path)

    def delete(self, path):
        self.model.remove(path)
