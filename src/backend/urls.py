from django.urls import path

from backend import views

urlpatterns = [
    path('software/list', views.get_software_list),
    path('software/details/<str:software_id>', views.get_software_details),
    path('software/bugs/<str:software_id>', views.get_software_bugs),
    path('bug', views.post_bug_add),
    path('bug/<int:bug_id>/', views.get_bug_details),
    path('bug_vote/<int:bug_id>/', views.get_bug_vote)
]
