import urllib3


class RequestManager():
    def __init__(self, rotateip=None, *args, **kwargs):
        self.manager = urllib3.PoolManager(*args, **kwargs)
        self.rotateIP = rotateip

    def request(self, *args, **kwargs):
        return self.manager.request(*args, **kwargs)