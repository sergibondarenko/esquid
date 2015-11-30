import json, re
from django.db import models
from elasticsearch import Elasticsearch
from elasticquery import ElasticQuery, Filter, Query, Aggregate

# Create your models here.

class Esearch(models.Model):
	
    size = 100
    must_fields = ""
    must_values = ""
    should_fields = ""
    should_values = ""
    mustnot_fields = ""
    mustnot_values = ""
    all_indexes = ""


    def init(self, host, port):
        self.host = host
        self.port = port


    def searchAll(self, index):
        self.index = index

        es = Elasticsearch(hosts = [{"host": self.host, "port": self.port}])
        res = es.search(index=index, body={"query": {"match_all": {}}})
        return res


    def freeSearch(self, searchquery, index):
        es = Elasticsearch(hosts = [{"host": self.host, "port": self.port}])

        #q = ElasticQuery(es=Elasticsearch(),index='shakespeare',doc_type='')
        q = ElasticQuery(es, index=index, doc_type='')

        #searchquery = raw_input("Search: ")
        ElasticQuery.sort(q,"_score",order="desc")
        ElasticQuery.size(q,100)
        
        if searchquery.count("\in ") <= 2 and searchquery.count("\\filter ") <= 1:
            # SELECT *** IN *** FILTER *** IN ***
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
            
            # SELECT *** IN *** FILTER ***
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
            
            # SELECT *** IN ***
            elif searchquery.count("\in ") == 1 and searchquery.find("\\filter ") == -1 and searchquery.find("\\filter") == -1:
                print searchquery[:searchquery.find("\in")]
                print searchquery[searchquery.find("\in") + 4:].replace(","," ").split()
                q.query(Query.query_string(
                    searchquery[:searchquery.find("\in")-1] + " AND " + 
                    searchquery[:searchquery.find("\in")-1].lower() + " AND " + 
                    searchquery[:searchquery.find("\in")-1].upper() + " AND " + 
                    searchquery[:searchquery.find("\in")-1].title(),
                    searchquery[searchquery.find("\in") + 4:].replace(","," ").split(),default_operator='AND'
                ))
    
            # SELECT ***
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
                print "Query Error :( -> Rewrite your query!"
        else:
            print "Query Error :( -> Rewrite your query!"
    
        #print q.json()
        return q.get()


    # Autoupdate
    def return_single_field_search(field,search):
        q = ElasticQuery(es=Elasticsearch(),index=all_indexes,doc_type='')
        q.aggregate(Aggregate.terms(search,field))
        q.query(Query.query_string(search,field,default_operator='OR',analyze_wildcard=True))
        q.fields(field)
        ElasticQuery.sort(q,"_score",order="desc")
        print q.get()
    

    # Filter output
    def return_values(query,start,end):
        count = query.count("(")
        indexes = ""
        while count > 0:
            indexes = indexes + query[query.index(start) + 1:query.index(end)] + ","
            if count != 1:
                query = query[query.index(")(") + 1:]
            count = count - 1
        return indexes[:len(indexes) - 1]
    

    # Filter output
    def remove_dupl(string):
        list_terms = []
        string = string.replace(","," ")
        list_terms = string.split()
        terms = ""
        for term in list_terms:
            if terms.find(term) == -1:
                terms = terms + term + ","
        return terms
    

    def return_elements(query,conditions,all_indexes):
        result = re.search('%' + conditions + '%.*?%', query).group()
        result = result[:len(result) - 2].replace('%' + conditions + '%',"")
        return result


    def logicalSearch(request, query):
        query = query.replace("MUST ","%MUST%").replace("SHOULD ","%SHOULD%").replace("MUST_NOT ","%MUST_NOT%") + " %"
        
        if query.find("%MUST%") != -1:
            result = return_elements(query,"MUST",all_indexes)
            must_fields = return_values(result,".","=")
            must_fields = must_fields[:len(remove_dupl(must_fields)) - 1]
            must_values = return_values(result,"=",")")
        
        if query.find("%SHOULD%") != -1:
            result = return_elements(query,"SHOULD",all_indexes)
            should_fields = return_values(result,".","=")
            should_fields = should_fields[:len(remove_dupl(should_fields)) - 1]
            should_values = return_values(result,"=",")")
        
        if query.find("%MUST_NOT%") != -1:
            result = return_elements(query,"MUST_NOT",all_indexes)
            mustnot_fields = return_values(result,".","=")
            mustnot_fields = mustnot_fields[:len(remove_dupl(mustnot_fields)) - 1]
            mustnot_values = return_values(result,"=",")")
        
        all_indexes = all_indexes + return_values(result,"(",".") + ','
        q = ElasticQuery(es=Elasticsearch(),index=all_indexes,doc_type='')
        ElasticQuery.sort(q,"_score",order="desc")
        ElasticQuery.size(q,str(size))
        
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
                
        elif must_fields != "" and should_fields == "" and mustnot_fields == "":
            q.query(Query.query_string(
                must_values + " OR " + 
                must_values.lower() + " OR " + 
                must_values.upper() + " OR " + 
                must_values.title(),
                must_fields,default_operator='AND'
            ))
        
        else:
            print "Query Error :( -> Rewrite your query!"
        
        #print q.json()
        return q.get()
