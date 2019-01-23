class MetricStore:
    store = None


    def __init__(self, *args):
        self.store = {}
        for metric_name in args:
            self.register_metric(metric_name)


    def register_metric(self, name):
        if name in self.store:
            raise ValueError("this metric is already in the store:", name)
        self.store[name] = []


    def record(self, name, value):
        if name in self.store:
            self.store[name].append(value)
        else:
            raise ValueError("this metric is not in the store:", name)


    def extract(self, name):
        return self.store.get(name, [])
