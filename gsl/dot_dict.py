class DotDict(dict):
    def __getattribute__(self, k):
        try:
            v = self[k]
        except KeyError:
            return super().__getattribute__(k)
        return v

    def __setattr__(self, k, v):
        try:
            self[k] = v
        except KeyError:
            return super().__setattr__(k, v)
