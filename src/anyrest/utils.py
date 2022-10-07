def filter(data, filters):
    # create key value tuples for each type.
    if type(data) is dict:
        kv = data.items()
    else:
        kv = enumerate(data)

    new = {}
    # Works for both types!
    for k, v in kv:
        match = True
        for f in filters:
            if str(v.get(f)) != filters[f]:
                match = False
                break
        if match:
            new[k] = data[k]

    if type(data) is list:
        new = list(new.values())

    return new

def fields(data, fields):
    if type(data) is dict:
        kv = data.items()
    else:
        kv = enumerate(data)

    new = {}

    for k, v in kv:
        for f in fields:
            if f in v:
                if not k in new:
                    new[k] = {}
                new[k][f] = v[f]

    if type(data) is list:
        new = list(new.values())

    return new

def sort(data, sorts):
    if not type(data) is list:
        return data

    keys = __getKeys(data, sorts)

    new = []
    for i, d in enumerate(data):
        new.append([keys[i], d])

    new.sort(key=(lambda x : x[0]))

    for i, d in enumerate(new):
        new[i] = d[1]

    return new

def __getKeys(data, sorts):
    keys = [()] * len(data)
    for sort in sorts:
        # Check if all types match.
        match = True
        t = None
        for e in data:
            if sort in e:
                if t == None:
                    t = type(e[sort])
                else:
                    if t != type(e[sort]):
                        match = False
                        break
            
        # Set the default value.
        if t is None:
            continue
        elif t is int or t is float:
            default = 0
        elif t is str:
            default = ""
        elif t is list:
            default = []
        elif t is bool:
            default = False
        else: # dict, ...
            match = False

        # If no match, convert all to string.
        if match:
            f = lambda e : e[sort] if sort in e else default
        else:
            f = lambda e : str(e[sort]) if sort in e else ""

        for i in range(len(data)):
            keys[i] = (*keys[i], f(data[i]))

    return keys
