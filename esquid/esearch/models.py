import json, re
from django.db import models
from elasticsearch import Elasticsearch
from elasticquery import ElasticQuery, Filter, Query, Aggregate

# Create your models here.

class Esearch(models.Model):
	
    def init(self, host, port):
        self.host = host
        self.port = port


    def searchAll(self, index):
        self.index = index

        es = Elasticsearch(hosts = [{"host": self.host, "port": self.port}])
        res = es.search(index=index, body={"query": {"match_all": {}}})
        return res


    def autoComplete(self, query, key, myindex, mysize):
        self.index = myindex
        values = []

        es = Elasticsearch(hosts = [{"host": self.host, "port": self.port}])

        query = '.*' + query + '.*'

        # UPPER case
        res = es.search(index = myindex, size = mysize, body = {"query": {"regexp": {key: query.upper()}}})
        for doc in res['hits']['hits']:
            values.append(doc['_source'][key])

        # lower case
        res = es.search(index = myindex, size = mysize, body = {"query": {"regexp": {key: query.lower()}}})
        for doc in res['hits']['hits']:
            values.append(doc['_source'][key])

        # Title case
        res = es.search(index = myindex, size = mysize, body = {"query": {"regexp": {key: query.title()}}})
        for doc in res['hits']['hits']:
            values.append(doc['_source'][key])

        values = sorted(set(values))    # Remove duplicates and sort

        return values

    # Code used to compose query_string with or without '"', based on wildcards find
    def compose_query(self,terms,fields):
        if terms.find("*") == -1 and terms.find("?") == -1:
            terms = terms.replace(',','" OR "')
            return Query.query_string(
                '("' + terms + '") OR (' + '"' + terms.lower() + '") OR (' + '"' + terms.upper() + '") OR (' + '"' + terms.title() + '")',
                fields=fields.replace(", ",",").replace(","," ").split(),lowercase_expanded_terms=False
            )
        else:
            return Query.query_string(
                terms + ' OR ' + terms.lower() + ' OR ' + terms.upper() + ' OR ' + terms.title(),
                fields=fields.replace(", ",",").replace(","," ").split(),lowercase_expanded_terms=False
            )


    def freeSearch(self, searchquery):
        # Elasticsearch connection initialization
        es = Elasticsearch(hosts = [{"host": self.host, "port": self.port}])
        size = 500
        index = ""
        # Find all indexes and remove them from the query
        if searchquery.find("\index") != -1:
            index = searchquery.replace(", ",",").replace(" ",",")[searchquery.find("\index") + 7:]
            searchquery = searchquery[:searchquery.find("\index")]
        q = ElasticQuery(es, index=index, doc_type='')
        ElasticQuery.sort(q,"_score",order="desc")
        ElasticQuery.size(q,size)
        
        # Check correct query syntax (query must have max 2 '\in' and max 1 '\filter')
        if searchquery.count("\in ") <= 2 and searchquery.count("\\filter ") <= 1:
            # Code for query creation like "SELECT *** IN *** FILTER *** IN ***"
            if searchquery.count("\in ") == 2 and searchquery.find("\\filter ") != -1:
                q.query(Query.bool(
                    must=[self.compose_query(searchquery[:searchquery.find("\in")-1],searchquery[searchquery.find("\in") + 4:searchquery.find("\\filter")])],
                    must_not=[self.compose_query(searchquery[searchquery.find("\\filter") + 8:searchquery.rfind("\in")-1],searchquery[searchquery.rfind("\in") + 4:])]
                ))
            
            # Code for query creation like "SELECT *** IN *** FILTER ***"
            elif searchquery.count("\in ") == 1 and searchquery.find("\\filter ") != -1:
                q.query(Query.bool(
                    must=[self.compose_query(searchquery[:searchquery.find("\in")],searchquery[searchquery.find("\in") + 4:searchquery.find("\\filter")])],
                    must_not=[self.compose_query(searchquery[searchquery.find("\\filter") + 8:],"_all")]
                ))
            
            # Code for query creation like "SELECT *** IN ***"
            elif searchquery.count("\in ") == 1 and searchquery.find("\\filter ") == -1 and searchquery.find("\\filter") == -1:
                q.query(self.compose_query(searchquery[:searchquery.find("\in")-1],searchquery[searchquery.find("\in") + 4:]))
    
            # Code for query creation like "SELECT ***"
            elif searchquery.count("\in ") == 0 and searchquery.count("\in") == 0 and searchquery.find("\\filter ") == -1 and searchquery.find("\\filter") == -1:
                q.query(self.compose_query(searchquery,"_all"))
            
            # ERROR
            else:
                return HttpResponse('Server: Wrong query syntax!')
        else:
            return HttpResponse('Server: Wrong query syntax!')

        print q.json()
        return q.get()


    # Autoupdate
    def return_single_field_search(field,search):
        q = ElasticQuery(es=Elasticsearch(),index=all_indexes,doc_type='')
        q.aggregate(Aggregate.terms(search,field))
        q.query(Query.query_string(search,field,default_operator='OR',analyze_wildcard=True))
        q.fields(field)
        ElasticQuery.sort(q,"_score",order="desc")
        print q.get()
    

    # Function that returns index name, fields name or values
    def return_values(self,query,start,end):
        count = query.count("(")
        indexes = ""
        while count > 0:
            indexes = indexes + query[query.index(start) + 1:query.index(end)] + ","
            if count != 1:
                query = query[query.index(")(") + 1:]
            count = count - 1
        return indexes[:-1]
    

    # Function that remove all duplicates found in a string
    def remove_dupl(self,string):
        list_terms = []
        string = string.replace(","," ")
        list_terms = string.split()
        terms = ""
        for term in list_terms:
            if terms.find(term) == -1:
                terms = terms + term + ","
        return terms
    
    # Function that splits the entire query into max three parts, each for MUST, SHOULD or MUST NOT condition
    def return_elements(self,query,conditions):
        result = re.search('%' + conditions + '%.*?%', query).group()
        result = result[:len(result)].replace('%' + conditions + '%',"")
        return result


    def logicalSearch(self,query):
        size = 500
        must_fields = ""
        must_values = ""
        should_fields = ""
        should_values = ""
        mustnot_fields = ""
        mustnot_values = ""
        all_indexes = ""

        # Remove space on query string and add % as prefix and suffix 
        query = query.replace("MUST ","%MUST%").replace("SHOULD ","%SHOULD%").replace("MUST_NOT ","%MUST_NOT%") + " %"
        
        # Populate class variables with values only if the relative condition is present on our query
        if query.find("%MUST%") != -1:
            result = self.return_elements(query,"MUST")
            must_fields = self.return_values(result,".","=")
            must_fields = must_fields[:len(self.remove_dupl(must_fields))]
            must_values = self.return_values(result,"=",")")
        if query.find("%SHOULD%") != -1:
            result = self.return_elements(query,"SHOULD")
            should_fields = self.return_values(result,".","=")
            should_fields = should_fields[:len(self.remove_dupl(should_fields))]
            should_values = self.return_values(result,"=",")")
        if query.find("%MUST_NOT%") != -1:
            result = self.return_elements(query,"MUST_NOT")
            mustnot_fields = self.return_values(result,".","=")
            mustnot_fields = mustnot_fields[:len(self.remove_dupl(mustnot_fields))]
            mustnot_values = self.return_values(result,"=",")")
        
        # Elasticsearch connection initialization
        all_indexes = self.return_values(result,"(",".")
        es = Elasticsearch(hosts = [{"host": self.host, "port": self.port}])
        q = ElasticQuery(es,index=self.remove_dupl(all_indexes),doc_type='')
        ElasticQuery.sort(q,"_score",order="desc")
        ElasticQuery.size(q,str(size))

        # Code for query creation like "MUST (...) SHOULD (...) MUST_NOT(...)"
        if must_fields != "" and should_fields != "" and mustnot_fields != "":
            q.query(Query.bool(
                must=[self.compose_query(must_values,must_fields)],
                should=[self.compose_query(should_values,should_fields)],
                must_not=[self.compose_query(mustnot_values,mustnot_fields)]
            ))
        
        # Code for query creation like "MUST (...) SHOULD (...)"
        elif must_fields != "" and should_fields != "" and mustnot_fields == "":
            q.query(Query.bool(
                must=[self.compose_query(must_values,must_fields)],
                should=[self.compose_query(should_values,should_fields)]
            ))
        
        # Code for query creation like "SHOULD (...) MUST_NOT(...)"
        elif must_fields == "" and should_fields != "" and mustnot_fields != "":
            q.query(Query.bool(
                should=[self.compose_query(should_values,should_fields)],
                must_not=[self.compose_query(mustnot_values,mustnot_fields)]
            ))
        
        # Code for query creation like "MUST (...) MUST_NOT(...)"
        elif must_fields != "" and should_fields == "" and mustnot_fields != "":
            q.query(Query.bool(
                must=[self.compose_query(must_values,must_fields)],
                must_not=[self.compose_query(mustnot_values,mustnot_fields)]
            ))
                
        # Code for query creation like "MUST (...)"
        elif must_fields != "" and should_fields == "" and mustnot_fields == "":
            q.query(Query.bool(
                must=[self.compose_query(must_values,must_fields)]
            ))
        
        # ERROR
        else:
            return HttpResponse('Server: Wrong query syntax!')
        
        return q.get()
