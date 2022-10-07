from google.cloud import firestore
from google.cloud.firestore import DocumentReference
from typing import Optional, Union
from .abstract_odr import AbstractOdr, dict
import os

PROJECT = os.environ.get("PROJECT")


class FirestoreOdr(AbstractOdr):
    def __init__(self, db: Optional[firestore.Client] = None):
        if db is None:
            self.db = firestore.Client(project=PROJECT)
        else:
            self.db = db

    def _dig(self, doc_ref: DocumentReference, depth: int = 0) -> dict:
        doc = doc_ref.get()
        cols = doc_ref.collections()
        data: Union[dict, None] = doc.to_dict()
        data = data if data else {}

        if not doc.exists:
            if depth == 0 and len(list(cols)) == 0:
                raise KeyError

        for col in cols:
            data[col.id] = {}
            for d in col.list_documents():
                data[col.id][d.id] = self._dig(d, depth=depth+1)

        return data

    def _getDoc(self, doc_ref: DocumentReference, recursive: bool) -> dict:
        if recursive:
            return self._dig(doc_ref)
        else:
            data = doc_ref.get()
            d: Union[dict, None] = data.to_dict()
            d = d if d else {}
            if not data.exists:
                # If document does not exist.
                raise KeyError
            else:
                return d

    def get(self, path: str, recursive: bool = True) -> dict:
        if len(path.split("/")) % 2 == 0:
            doc_ref = self.db.document(path)
            return self._getDoc(doc_ref, recursive)
        else:
            col_ref = self.db.collection(path)
            docsl = list(col_ref.list_documents())

            if len(docsl) == 0:
                raise KeyError
            data = {}
            for doc in docsl:
                data[doc.id] = self._getDoc(doc, recursive)

            return data

    def set(self, path: str, data: dict) -> dict:
        doc_ref = self.db.document(path)
        doc_ref.set(data)
        return data

    def update(self, path: str, data: dict) -> dict:
        doc_ref = self.db.document(path)
        doc_ref.set(data, merge=True)
        return self.get(path)

    def delete(self, path: str) -> None:
        if len(path.split("/")) % 2 == 0:
            ref = self.db.document(path)
        else:
            ref = self.db.collection(path)

        self.db.recursive_delete(
                reference=ref,
                bulk_writer=self.db.bulk_writer()
                )
