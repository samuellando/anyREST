import pytest
from anyrest.firestore_odr import FirestoreOdr 
from mockfirestore import MockFirestore
from anyrest.model import Model

TOKEN = "testtoken"
BASE = f'tokens/{TOKEN}/'

@pytest.fixture()
def db():
    db = MockFirestore()
    db.reset()
    return db

@pytest.fixture()
def model(db):
    odr = FirestoreOdr(db)
    model = Model(TOKEN, odr)
    return model

@pytest.mark.parametrize("path,data", [
        ("this/is/an/example/path/0", {"test": "data"}),
        ("this/is/an/example/path/doc", {"test": "data"})
        ])
class TestCases:
    def test_read_existing(self, model, db, path, data):
        db.document(BASE+path).set(data)
        assert model.read(path) == data

    def test_read_nonexisting(self, model, db, path, data):
        with pytest.raises(KeyError):
            model.read(path)

    def test_insert_existsing(self, model, db, path, data):
        id = path.split("/")[-1]
        colpath = "/".join(path.split("/")[:-1])
        try:
            id = str(int(id) + 1)
        except:
            id = "0"
        db.document(BASE+path).set(data)
        r = model.insert(data, colpath)
        assert r == data
        r = db.document(f'{BASE}{colpath}/{id}').get().to_dict()
        assert r == data

    def test_insert_nonexisting(self, model, db, path, data):
        id = "0"
        colpath = "/".join(path.split("/")[:-1])
        r = model.insert(data, colpath)
        assert r == data
        r = db.document(f'{BASE}{colpath}/{id}').get().to_dict()
        assert r == data

    def test_write(self, model, db, path, data):
        r = model.write(data, path)
        assert r == data
        r = db.document(f'{BASE}{path}').get().to_dict()
        assert r == data

    def test_update_existsing(self, model, db, path, data):
        db.document(BASE+path).set(data)
        r = model.update({"new": "newdata"}, path)
        data["new"] = "newdata"
        assert r == data
        r = db.document(f'{BASE}{path}').get().to_dict()
        assert r == data

    def test_update_nonexisting(self, model, db, path, data):
        r = model.update(data, path)
        assert r == data
        r = db.document(f'{BASE}{path}').get().to_dict()
        assert r == data

    def test_delete(self, model, db, path, data):
        db.document(BASE+path).set(data)
        model.remove(path)
        r = db.document(BASE+path).get()
        assert not r.exists 
