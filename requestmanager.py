import urllib3


class RequestManager():
    def __init__(self, proxy_host=None, proxy_port=8080, *args, **kwargs):
        self.retries = urllib3.util.Retry(connect=1)
        if proxy_host:
            self.manager = urllib3.ProxyManager(f"http://{proxy_host}:{proxy_port}/", retries=self.retries, *args, **kwargs)
        else:
            self.manager = urllib3.PoolManager(retries=self.retries, *args, **kwargs)

    def request(self, *args, **kwargs):
        return self.manager.request(*args, **kwargs)