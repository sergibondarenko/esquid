import json
from django.db import models
from elasticsearch import Elasticsearch

# Create your models here.

class Esearch(models.Model):
	
    def init(self, host, port):
        self.host = host
        self.port = port

    def search_all(self, index):
        self.index = index

        es = Elasticsearch(hosts = [{"host": self.host, "port": self.port}])
        res = es.search(index=index, body={"query": {"match_all": {}}})
        return res

