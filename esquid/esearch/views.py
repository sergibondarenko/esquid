from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse

from .models import Esearch

# Create your views here.
Esearch = Esearch()

class IndexView(generic.ListView):
    template_name = 'esearch/index.html'
    context_object_name = 'results_list'

    def get_queryset(self):
        res = Esearch.search_all()
        return res

#def index(request):
#	res = Esearch.search_all()
#	#return HttpResponse(res['hits']['hits'][0]['_source']['email'])
#
#	first_name = []
#	for person in res['hits']['hits']:
#		first_name.append(person['_source'].get('first_name'))
#		
#	context = {'results_list': res, 'first_name': first_name}
#	return render(request, 'esearch/index.html', context)
	
