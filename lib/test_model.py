import unittest
import time
import shutil
import os


from model import Model

class testModel(unittest.TestCase):
    def setUp(self):
        self.data = "testData"
        self.token = "testtoken"
        self.model = Model(self.token, self.data)
 
        # recreate the dir. 
        cwd = os.getcwd()
        path = os.path.join(cwd, self.data)
       
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
        os.makedirs(path)

    def tearDown(self):
        cwd = os.getcwd()
        path = os.path.join(cwd, self.data)
       
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass

    def test_write(self):
        # Write at base.
        try:
            wdata = self.model.write({"libs": {"0": {"cols": {"0": {"name": "Sam"}}}}})
        except:
            self.assertTrue(False)
            return 
        if wdata != None:
            self.assertTrue(wdata["libs"]["0"]["cols"]["0"]["name"] == "Sam")
        else:
            self.assertTrue(False)

        data = self.model.read("libs/0/cols/0".split("/"))
        self.assertTrue(data["name"] == "Sam")

        # Write at layer.
        try:
            wdata = self.model.write({"name": "Fabio"}, "libs/0/cols/1".split("/"))
        except:
            self.assertTrue(False)
            return 
        if wdata != None:
            self.assertTrue(wdata["name"] == "Fabio")
        else:
            self.assertTrue(False)

        data = self.model.read("libs/0/cols/1".split("/"))
        self.assertTrue(data["name"] == "Fabio")

        # Write on non exitant layers.
        with self.assertRaises(Exception):
                self.model.write({"name": "Fabio"}, "cols/0/dne")

    def test_insert(self):
        try:
            wdata = self.model.insert({"name": "Sam"}, "libs/0/cols".split("/"))
        except:
            self.assertTrue(False)
            return
        if wdata != None:
            self.assertTrue(wdata["name"] == "Sam")
        else:
            self.assertTrue(False)
        data = self.model.read("libs/0/cols/0".split("/"))
        self.assertTrue(data["name"] == "Sam")

        self.model.write({"name": "Fabio"}, "libs/0/cols/test".split("/"))

        try:
            wdata = self.model.insert({"name": "Mariano"}, "libs/0/cols".split("/"))
        except:
            self.assertTrue(False)
            return
        if wdata != None:
            self.assertTrue(wdata["name"] == "Mariano")
        else:
            self.assertTrue(False)
        data = self.model.read("libs/0/cols/1".split("/"))
        self.assertTrue(data["name"] == "Mariano")


    def test_remove(self):
        self.model.insert({"name": "Sam"}, "libs/0/cols".split("/"))
        self.model.insert({"name": "Fabio"}, "libs/0/cols".split("/"))
        self.model.insert({"name": "Mariano"}, "libs/0/cols".split("/"))

        self.model.remove("libs/0/cols/1".split("/"))

        self.model.read("libs/0/cols/0".split("/"))
        self.model.read("libs/0/cols/2".split("/"))
        try:
            self.model.read("libs/o/cols/1".split("/"))
            self.assertTrue(False)
            return
        except:
            pass

    def test_read(self):
        self.model.insert({"name": "Sam"}, "libs/0/cols".split("/"))

        try:
            data = self.model.read("libs/0/cols/0".split("/"))
        except:
            self.assertTrue(False)
            return

        if data != None:
           self.assertTrue(data["name"] == "Sam")
        else:
            self.assertTrue(False)

        with self.assertRaises(Exception):
            self.model.read("libs/0/cols/1".split("/"))


if __name__ == "__main__":
    unittest.main()
