from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^updateuser', views.UpdateUser, name='updateUser'),
    #url(r'^renderiframe/$', views.Iframe, name='Iframe'),
    url(r'^query/$', views.Querys, name='Query'),
    url(r'^$', views.Index, name='Index'),
    url(r'^cancelbutton', views.Cancel, name='Cancel'),
    url(r'^queryfeedback/(?P<query_id>[0-9]+)/(?P<user_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/like$',views.QueryFeedbackLike),
    url(r'^queryfeedback/(?P<query_id>[0-9]+)/(?P<user_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/dislike$',views.QueryFeedbackDislike),
    url(r'^analytics$',views.Analytics),
    url(r'^getanalysis',views.GetAnalysis),
    url(r'^report/(?P<from_date>[0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9])/(?P<to_date>[0-9][0-9]\/[0-9][0-9]\/[0-9][0-9][0-9][0-9])/$',views.Report),
    url(r'^pc_id', views.GetPcId),
    url(r'^get_dictionary',views.GetDictionary),
    url(r'^deleteEntities', views.deleteEntities)
]

