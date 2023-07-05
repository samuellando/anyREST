# AnyREST 
- A ready to deploy API endpoint that accepts, stores and returns any data.
- Suppors authentication with OAuth2 and api-keys
- Supports mondoDB and Firebase.
- Has a mock backend for unit testing.

# Quick Start
## Installation
```bash
pip install https://github.com/samuellando/anyREST.git
```

## Running the server in mock (test) mode
```bash
python -m anyrest
```

## Wrapping AnyREST with a flask application, and using a backend Database
main.py
```python
import anyrest
import os
from flask import Flask

app = Flask(__name__)

# Firebase
firebase_app = firebase_admin.initialize_app(options={'projectId': '<PROJECT_ID>'})
db = firestore.client()
ar = anyrest.addAnyrestHandlersFirestore(app, db, [<Authority>, <Audience>, lock=True])

# MongoDB
uri = "mongodb+srv://{}:{}@<URI>/?retryWrites=true&w=majority".format(os.environ["MONGODB_USER"], os.environ["MONGODB_PASSWORD"])
client = MongoClient(uri,
  tls=True,
  server_api=ServerApi('1'))
db = client[<DATABASE>]
ar = anyrest.addAnyrestHandlersMongoDB(app, db, [<Authority>, <Audience>, lock=True])

# Avalable functions for use in other handlers.
ar.get(<PATH>)
ar.query(<PATH>, <QUERY>)
ar.post(<PATH>, data)
ar.put(<PATH>, data)
ar.patch(<PATH>, data)
ar.delete(<PATH>)
```

## Notes on query
- firestores's query accepts an array of filters like `[(feild, "==", 10)]` and are then chained together with `.where`
- mongoDB accepts an array, with up to 3 elements `[mondodb query, sort or None, limit]`
