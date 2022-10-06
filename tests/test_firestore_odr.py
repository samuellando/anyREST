import pytest
from anyrest.firestore_odr import Odr
from mockfirestore import MockFirestore


@pytest.fixture()
def db():
    db = MockFirestore()
    db.reset()
    return db

@pytest.fixture()
def odr(db):
    odr = Odr(db)
    return odr

@pytest.mark.parametrize("path,data", [
        ("this/is/an/example/path/0", {"test": "data"})
        ])
class TestCases:
    def test_set(self, path, data, odr, db):
        ret = odr.set(path, data)
        assert ret == data
        r = db.document(path).get()
        assert r.exists
        d = r.to_dict()
        for k in data:
            assert d[k] == data[k]

    def test_get_existing_data(self, path, data, odr, db):
        db.document(path).set(data)
        d = odr.get(path)
        for k in data:
            assert d[k] == data[k]
        assert d["test"] == "data"

    def test_get_existing_data_nonrecursive(self, path, data, odr, db):
        db.document(path).set(data)
        d = odr.get(path, recursive=False)
        for k in data:
            assert d[k] == data[k]
        assert d["test"] == "data"

    def test_get_existing_data_and_children(self, path, data, odr, db):
        db.document(path).set(data)
        d = odr.get(path.split("/")[0])
        for p in path.split("/")[1:]:
            assert list(d.keys())[0] == p
            d = d[p]
        for k in data:
            assert d[k] == data[k]
    
    def test_update_existsing_data(self, path, data, odr, db):
        db.document(path).set(data)

        insert = {"new": "newData"}
        ret = odr.update(path, insert)
        for k in data:
            insert[k] = data[k]
        assert ret == insert

        r = db.document(path).get()
        assert r.exists
        d = r.to_dict()
        for k in data:
            assert d[k] == data[k]
        assert d["new"] == "newData"

    def test_delete_existing_data(self, path, data, odr, db):
        db.document(path).set(data)
        r = db.document(path).get()
        assert r.exists
        odr.delete(path)
        r = db.document(path).get()
        assert not r.exists

    def test_delete_existing_data_collection(self, path, data, odr, db):
        db.document(path).set(data)
        r = db.document(path).get()
        assert r.exists
        colpath = "/".join(path.split("/")[:-1])
        odr.delete(colpath)
        r = db.document(path).get()
        assert not r.exists


    def test_get_nonexisting_data(self, path, data, odr):
        with pytest.raises(KeyError):
            odr.get(path)

    def test_get_nonexisting_data_nonrecursive(self, path, data, odr):
        with pytest.raises(KeyError):
            odr.get(path, recursive=False)

    def test_get_nonexisting_collection(self, path, data, odr):
        with pytest.raises(KeyError):
            odr.get(path+"/col")
    
    def test_update_nonexistsing_data(self, path, data, odr, db):
        insert = {"new": "newData"}
        ret = odr.update(path, insert)
        assert ret == insert

        r = db.document(path).get()
        assert r.exists
        d = r.to_dict()
        for k in data:
            assert not k in d
        assert d["new"] == "newData"

    def test_delete_nonexisting_data(self, path, data, odr, db):
        odr.delete(path)
        r = db.document(path).get()
        assert not r.exists
