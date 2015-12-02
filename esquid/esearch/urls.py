from django.conf.urls import url

from . import views

urlpatterns = [
	#url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^$', views.index, name='index'),
	url(r'^postmenu/$', views.postmenu, name='postmenu'),
	url(r'^livesearch/$', views.livesearch, name='livesearch'),
	url(r'^search_all/$', views.search_all, name='search_all'),
	url(r'^freesearch/$', views.freesearch, name='freesearch'),
	url(r'^logicalsearch/$', views.logicalsearch, name='logicalsearch'),
	url(r'^autocomplete/$', views.autocomplete, name='autocomplete'),
]
