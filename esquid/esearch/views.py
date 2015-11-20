from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views import generic

from .models import Esearch

# Create your views here.
Esearch = Esearch()

def index(request):
	res = Esearch.search_all()
	#return HttpResponse(res['hits']['hits'][0]['_source']['email'])

	context = {'results_list': res}
	return render(request, 'esearch/index.html', context)
	
