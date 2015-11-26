from django.conf.urls import url

from . import views

urlpatterns = [
	#url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^$', views.index, name='index'),
	url(r'^postmenu/$', views.postmenu, name='postmenu'),
	url(r'^livesearch/$', views.livesearch, name='livesearch'),
]
