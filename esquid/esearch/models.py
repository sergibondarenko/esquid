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

        query += '.*'

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



    def freeSearch(self, searchquery):
        # Elasticsearch connection initialization
        es = Elasticsearch(hosts = [{"host": self.host, "port": self.port}])
        # q = ElasticQuery(es=Elasticsearch(),index='shakespeare',doc_type='')
        index = ""
        # Find all indexes and remove them from the query
        if searchquery.find("\index") != -1:
            index = searchquery.replace(", ",",").replace(" ",",")[searchquery.find("\index") + 7:]
            searchquery = searchquery[:searchquery.find("\index")]
        q = ElasticQuery(es, index=index, doc_type='')
        ElasticQuery.sort(q,"_score",order="desc")
        ElasticQuery.size(q,100)
        
        # Check correct query syntax (query must have max 2 '\in' and max 1 '\filter')
        if searchquery.count("\in ") <= 2 and searchquery.count("\\filter ") <= 1:
            # Code for query creation like "SELECT *** IN *** FILTER *** IN ***"
            if searchquery.count("\in ") == 2 and searchquery.find("\\filter ") != -1:
                q.query(Query.bool(
                    must=[Query.query_string(
                        searchquery[:searchquery.find("\in")] + " OR " + 
                        searchquery[:searchquery.find("\in")].lower() + " OR " + 
                        searchquery[:searchquery.find("\in")].upper() + " OR " + 
                        searchquery[:searchquery.find("\in")].title(),
                        searchquery[searchquery.find("\in") + 4:searchquery.find("\\filter")].replace(","," ").split(),default_operator='AND'
                    )],
                    must_not=[Query.query_string(
                        searchquery[searchquery.find("\\filter") + 8:searchquery.rfind("\in")] + " OR " + 
                        searchquery[searchquery.find("\\filter") + 8:searchquery.rfind("\in")].lower() + " OR " + 
                        searchquery[searchquery.find("\\filter") + 8:searchquery.rfind("\in")].upper() + " OR " + 
                        searchquery[searchquery.find("\\filter") + 8:searchquery.rfind("\in")].title(),
                        searchquery[searchquery.rfind("\in") + 4:].replace(","," ").split(),default_operator='AND'
                    )]
                ))
            
            # Code for query creation like "SELECT *** IN *** FILTER ***"
            elif searchquery.count("\in ") == 1 and searchquery.find("\\filter ") != -1:
                q.query(Query.bool(
                    must=[Query.query_string(
                        searchquery[:searchquery.find("\in")] + " OR " + 
                        searchquery[:searchquery.find("\in")].lower() + " OR " + 
                        searchquery[:searchquery.find("\in")].upper() + " OR " + 
                        searchquery[:searchquery.find("\in")].title(),
                        searchquery[searchquery.find("\in") + 4:searchquery.find("\\filter")],default_operator='AND'
                    )],
                    must_not=[Query.query_string(
                        searchquery[searchquery.find("\\filter") + 8:] + " OR " + 
                        searchquery[searchquery.find("\\filter") + 8:].lower() + " OR " + 
                        searchquery[searchquery.find("\\filter") + 8:].upper() + " OR " + 
                        searchquery[searchquery.find("\\filter") + 8:].title(),
                        "_all",default_operator='AND'
                    )]
                ))
            
            # Code for query creation like "SELECT *** IN ***"
            elif searchquery.count("\in ") == 1 and searchquery.find("\\filter ") == -1 and searchquery.find("\\filter") == -1:
                q.query(Query.query_string(
                    searchquery[:searchquery.find("\in")-1] + " AND " + 
                    searchquery[:searchquery.find("\in")-1].lower() + " AND " + 
                    searchquery[:searchquery.find("\in")-1].upper() + " AND " + 
                    searchquery[:searchquery.find("\in")-1].title(),
                    searchquery[searchquery.find("\in") + 4:].replace(","," ").split(),default_operator='AND'
                ))
    
            # Code for query creation like "SELECT ***"
            elif searchquery.count("\in ") == 0 and searchquery.count("\in") == 0 and searchquery.find("\\filter ") == -1 and searchquery.find("\\filter") == -1:
                q.query(Query.match(
                    "_all",(
                        searchquery + " OR " + 
                        searchquery.lower() + " OR " + 
                        searchquery.upper() + " OR " + 
                        searchquery.title(),
                    )
                ))
            
            # ERROR
            else:
                return HttpResponse('Server: Wrong query syntax!')
        else:
            return HttpResponse('Server: Wrong query syntax!')
    
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
        return indexes[:len(indexes) - 1]
    

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
        result = result[:len(result) - 2].replace('%' + conditions + '%',"")
        return result


    def logicalSearch(self,query):
        size = 100
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
            must_fields = must_fields[:len(self.remove_dupl(must_fields)) - 1]
            must_values = self.return_values(result,"=",")")
        if query.find("%SHOULD%") != -1:
            result = self.return_elements(query,"SHOULD")
            should_fields = self.return_values(result,".","=")
            should_fields = should_fields[:len(self.remove_dupl(should_fields)) - 1]
            should_values = self.return_values(result,"=",")")
        if query.find("%MUST_NOT%") != -1:
            result = self.return_elements(query,"MUST_NOT")
            mustnot_fields = self.return_values(result,".","=")
            mustnot_fields = mustnot_fields[:len(self.remove_dupl(mustnot_fields)) - 1]
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
                        must=[Query.query_string(
                            must_values + " OR " + 
                            must_values.lower() + " OR " + 
                            must_values.upper() + " OR " + 
                            must_values.title(),
                            must_fields,default_operator='AND'
                        )],
                        should=[Query.query_string(
                            should_values + " OR " + 
                            should_values.lower() + " OR " + 
                            should_values.upper() + " OR " + 
                            should_values.title(),
                            should_fields,default_operator='AND'
                        )],
                        must_not=[Query.query_string(
                            mustnot_values + " OR " + 
                            mustnot_values.lower() + " OR " + 
                            mustnot_values.upper() + " OR " + 
                            mustnot_values.title(),
                            mustnot_fields,default_operator='AND'
                        )]
                    ))
        
        # Code for query creation like "MUST (...) SHOULD (...)"
        elif must_fields != "" and should_fields != "" and mustnot_fields == "":
            q.query(Query.bool(
                        must=[Query.query_string(
                            must_values + " OR " + 
                            must_values.lower() + " OR " + 
                            must_values.upper() + " OR " + 
                            must_values.title(),
                            must_fields,default_operator='AND'
                        )],
                        should=[Query.query_string(
                            should_values + " OR " + 
                            should_values.lower() + " OR " + 
                            should_values.upper() + " OR " + 
                            should_values.title(),
                            should_fields,default_operator='AND'
                        )]
                    ))
        
        # Code for query creation like "SHOULD (...) MUST_NOT(...)"
        elif must_fields == "" and should_fields != "" and mustnot_fields != "":
            q.query(Query.bool(
                        should=[Query.query_string(
                            should_values + " OR " + 
                            should_values.lower() + " OR " + 
                            should_values.upper() + " OR " + 
                            should_values.title(),
                            should_fields,default_operator='AND'
                        )],
                        must_not=[Query.query_string(
                            mustnot_values + " OR " + 
                            mustnot_values.lower() + " OR " + 
                            mustnot_values.upper() + " OR " + 
                            mustnot_values.title(),
                            mustnot_fields,default_operator='AND'
                        )]
                    ))
        
        # Code for query creation like "MUST (...) MUST_NOT(...)"
        elif must_fields != "" and should_fields == "" and mustnot_fields != "":
            q.query(Query.bool(
                        must=[Query.query_string(
                            must_values + " OR " + 
                            must_values.lower() + " OR " + 
                            must_values.upper() + " OR " + 
                            must_values.title(),
                            must_fields,default_operator='AND'
                        )],
                        must_not=[Query.query_string(
                            mustnot_values + " OR " + 
                            mustnot_values.lower() + " OR " + 
                            mustnot_values.upper() + " OR " + 
                            mustnot_values.title(),
                            mustnot_fields,default_operator='AND'
                        )]
                    ))
                
        # Code for query creation like "MUST (...)"
        elif must_fields != "" and should_fields == "" and mustnot_fields == "":
            q.query(Query.query_string(
                must_values + " OR " + 
                must_values.lower() + " OR " + 
                must_values.upper() + " OR " + 
                must_values.title(),
                must_fields,default_operator='AND'
            ))
        
        # ERROR
        else:
            return HttpResponse('Server: Wrong query syntax!')
        
        return q.get()
