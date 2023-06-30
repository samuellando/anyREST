AnyREST is a API endpoint that accepts, stores and returns any data. 

It's purpose is to act as a mock backend, but it can also be used in production environments for projects with non-strict requirements.

It wraps a flask application, and optionally adds some authentication with Oauth2, and some general handlers.

Initializing also returns a handlers object with protected get, post, put, patch and query

Currently supports firestore and mongoBD as backends, the only difference between the two is their query methods.
- firestores's query accepts an array of filters like `[(feild, "==", 10)]` and are then chained together with `.where`
- mongoDB accepts an array, with up to 3 elements `[mondodb query, sort or None, limit]`
