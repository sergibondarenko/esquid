import json
from django.db import models
from elasticsearch import Elasticsearch

# Create your models here.

class Esearch(models.Model):
	
	def search_all(self):
		es = Elasticsearch(hosts = [{"host": "localhost", "port": "9200"}])
		res = es.search(index="facebook", body={"query": {"match_all": {}}})
		#print(res)
		#res = 'HELLO'
		return res

#def esearch():
#	es = Elasticsearch(hosts = [{"host": "localhost", "port": "9200"}])
#	res = es.search(index="facebook", body={"query": {"match_all": {}}})
#	return res
#
#print(esearch())
