from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from . import views

urlpatterns = [
	#url(r'^$', views.index, name='index')
	#url(r'^$', views.IndexView.as_view(), name='index'),
	#url(r'^postmenu/$', ensure_csrf_cookie(views.postmenu), name='postmenu'),
	url(r'^$', views.index, name='index'),
	url(r'^postmenu/$', views.postmenu, name='postmenu'),
]
