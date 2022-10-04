from google.cloud import firestore
import os

PROJECT = os.environ.get("PROJECT")

class Odr:
    def __init__(self, db=None):
        if db is None:
            self.db = firestore.Client(project=PROJECT)
        else:
            self.db = db

    def _dig(self, doc_ref, depth=0):
        doc = doc_ref.get()
        cols = doc_ref.collections()
        if doc.exists:
            data = doc.to_dict()
        else:
            if depth == 0 and len(list(cols)) == 0:
                raise Exception("Not found.")
            data = {}
        for col in cols:
            print(f'In col {col.id}')
            data[col.id] = {}
            for d in col.list_documents():
                print(f'\t{d.id}')
                data[col.id][d.id] = self._dig(d, depth=depth+1)

        return data

    def _getDoc(self, doc_ref, recursive):
        if recursive:
            return self._dig(doc_ref)
        else:
            data = doc_ref.get()
            if not data.exists:
                raise Exception("Not found.")
            else:
                return data.to_dict()

    def get(self, path, recursive=True):
        if len(path.split("/")) % 2 == 0:
            doc_ref = self.db.document(path)
            return self._getDoc(doc_ref, recursive)
        else:
            col_ref = self.db.collection(path)
            docsl = list(col_ref.list_documents())

            if len(docsl) == 0:
                raise Exception("Not found.")
            data = {}
            for doc in docsl:
                data[doc.id] = self._getDoc(doc, recursive)

            return data

    def set(self, path, data):
        doc_ref = self.db.document(path)
        doc_ref.set(data)
        return data

    def update(self, path, data):
        doc_ref = self.db.document(path)
        doc_ref.set(data, merge=True)
        return self.get(path)

    def delete(self, path):
        if len(path.split("/")) % 2 == 0:
            ref = self.db.document(path)
        else:
            ref = self.db.collection(path)
        print(ref)
        self.db.recursive_delete(reference=ref, bulk_writer=self.db.bulk_writer())

