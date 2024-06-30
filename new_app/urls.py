from django.urls import path

from new_app import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('', views.employee_list, name='employee_list'),
    path('add/', views.employee_add, name='employee_add'),
    path('search/', views.employee_search, name='employee_search'),

]