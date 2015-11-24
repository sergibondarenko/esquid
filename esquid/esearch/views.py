from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views import generic
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie, csrf_protect

from .models import Esearch

# Create your views here.
Esearch = Esearch()

def index(request):
	res = Esearch.search_all()
	#return HttpResponse(res['hits']['hits'][0]['_source']['email'])

	first_name = []
	for person in res['hits']['hits']:
		first_name.append(person['_source'].get('first_name'))
		
	context = {'results_list': res, 'first_name': first_name}
	return render(request, 'esearch/index.html', context)

def postmenu(request):
     if request.method == 'POST':
         if request.is_ajax():
             message = request.POST['msg']
             return HttpResponse(str(message))
             #return HttpResponse('Hello you!!!')
         else:
             raise Http404
     else:
         return HttpResponse('Nothing to return from server.')
    
#@csrf_exempt
#class IndexView(generic.ListView):
#    template_name = 'esearch/index.html'
#    context_object_name = 'results_list'
#
#    #@csrf_exempt
#    def get_queryset(self):
#        res = Esearch.search_all()
#        return res

#def postmenu(request):
#    return HttpResponse('Hello you!!!')

	
