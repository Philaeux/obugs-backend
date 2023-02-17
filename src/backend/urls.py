from django.urls import path

from backend import views

urlpatterns = [
    path('', views.index, name='index'),
    path('software/list', views.get_software_list),
    path('software/details/<str:software_id>', views.get_software_details),
]
