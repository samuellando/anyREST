import unittest
import shutil
import os


from anyrest.viewModel import ViewModel

class testModel(unittest.TestCase):
    def setUp(self):
        self.data = "testData"
        self.token = "testtoken"
        self.model = ViewModel(self.token, self.data)
 
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

    def test_create(self):
        self.model.create({"name": "Sam"}, "libs/0/cols")

        data = self.model.read("libs/0/cols/0")

        if type(data) is dict:
            self.assertEqual(data["name"], "Sam")

    def test_read(self):
        self.model.create({"name": "Sam"}, "libs/0/cols")
        self.model.create({"name": "Fabio"}, "libs/0/cols")

        data = self.model.read("libs/0/cols")
        self.assertTrue(type(data) is list)

        self.model.update({"name": "Fabio"}, "libs/0/cols/test")

        data = self.model.read("libs/0/cols")
        self.assertTrue(type(data) is dict)

    def test_update(self):
        with self.assertRaises(Exception):
            self.model.update({"name": "Sam"}, "libs/0/cols")

        self.model.create({"name": "Sam"}, "libs/0/cols")
        self.model.update({"name": "Fabio"}, "libs/0/cols/0")

        data = self.model.read("libs/0/cols/0")

        if type(data) is dict:
            self.assertEqual(data["name"], "Fabio")

    def test_delete(self):
        self.model.create({"name": "Sam"}, "libs/0/cols")

        self.model.delete("libs/0/cols/0")

        with self.assertRaises(Exception):
            data = self.model.read("libs/0/cols/0")
            print(data)

if __name__ == "__main__":
    unittest.main()
