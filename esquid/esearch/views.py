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
        Esearch.init('localhost', '9200');
	result = Esearch.search_all('shakespeare')

	context = {'results_list': result}
	return render(request, 'esearch/index.html', context)

def postmenu(request):
     if request.method == 'POST':
         if request.is_ajax():
             message = request.POST['msg']
             return HttpResponse(str(message))
         else:
             raise Http404
     else:
         return HttpResponse('Nothing to return from server.')
    
	
