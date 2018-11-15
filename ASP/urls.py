from django.urls import path
from ASP import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from django.conf import settings
from django.conf.urls import url
from django.http import HttpResponse

urlpatterns =\
[
    path('clinicmanager', views.CMViewsSupply.as_view(), name='clinic-manager'),
    path('clinicmanager/add_order', views.CMViewsSupply.construct_order, name='CM-add-order'),

    path('warehouse', views.WHViewsQueue.as_view(), name='warehouse'),
    path('warehouse/update', views.WHViewsQueue.update, name='WH-update'),
    path('warehouse/generate_rfid', views.WHViewsQueue.get_rfid, name='WH-generate_rfid'),

    path('dispatcher', views.DPViewsOrder.as_view(), name='dispatcher'),
    path('dispatcher/update_order', views.DPViewsOrder.update_order, name='DP-update-order'),
    path('dispatcher/generate_csv', views.DPViewsOrder.get_csv, name='DP-generate_csv'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.login, name='login'),
    url(r'^$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),

]

# showing image
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

