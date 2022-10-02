import unittest

from utils import filter, fields, sort

class testUtils(unittest.TestCase):
    def setUp(self):
        self.d = {
            "0": {
                "name": "b",
                "age": 2,
                "id": 0
            },
            "1": {
                "name": "a",
                "age": 2,
                "id": 1
            },
            "2": {
                "name": "b",
                "age": 1,
                "id": 2
            },
            "3": {
                "name": "a",
                "age": 1,
                "id": 3
            }
        }

        self.l = list(self.d.values())

    def test_sort(self):
        data = sort(self.l, ["age", "name"])

        self.assertEqual(data[0]["name"], "a")
        self.assertEqual(data[0]["age"], 1)

        self.assertEqual(data[1]["name"], "b")
        self.assertEqual(data[1]["age"], 1)

        self.assertEqual(data[2]["name"], "a")
        self.assertEqual(data[2]["age"], 2)

        self.assertEqual(data[3]["name"], "b")
        self.assertEqual(data[3]["age"], 2)

    def test_filter(self):
        data = filter(self.l, {"age": "2", "name": "a"})
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "a")
        self.assertEqual(data[0]["age"], 2)


        data = filter(self.d, {"age": "2", "name": "a"})
        self.assertEqual(len(data), 1)
        self.assertEqual(data["1"]["name"], "a")
        self.assertEqual(data["1"]["age"], 2)

    def test_fields(self):
        data = fields(self.l, ["age", "id"])
        self.assertEqual(len(data), 4)
        self.assertEqual(data[0].get("age"), 2)
        self.assertEqual(data[0].get("id"), 0)
        self.assertEqual(data[0].get("Name"), None)


        data = fields(self.d, ["age", "id"])
        self.assertEqual(len(data), 4)
        self.assertEqual(data["0"].get("age"), 2)
        self.assertEqual(data["0"].get("id"), 0)
        self.assertEqual(data["0"].get("Name"), None)

if __name__ == "__main__":
    unittest.main()
