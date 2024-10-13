from django.urls import path

from new_app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('indexx', views.indexx, name='indexx'),
    path('login', views.login, name='login'),
    path('industry', views.industry, name='industry'),
    path('consumer', views.consumer, name='consumer'),
    path('consumer_registration', views.consumer_registration, name='consumer_registration'),
    path('industry_registration', views.industry_registration, name='industry_registration'),
    path('adminbase', views.adminbase, name='adminbase'),
    path('consumerbase', views.consumerbase, name='consumerbase'),
    path('industrybase', views.industrybase, name='industrybase'),
    path('view_consumer', views.view_consumer, name='view_consumer'),
    path('view_industry', views.view_industry, name='view_industry'),
    path('admin_view_industry', views.admin_view_industry, name='admin_view_industry'),
    path('admin_view_consumer', views.admin_view_consumer, name='admin_view_consumer'),

    path('add_industry', views.add_industry, name='add_industry'),
    path("update_industry/<int:id>/", views.update_industry, name="update_industry"),
    path('delete_industry/<int:id>/', views.delete_industry, name='delete_industry'),

    path('approve_industry/<int:user_id>/', views.approve_industry, name='approve_industry'),
    path('reject_industry/<int:user_id>/', views.reject_industry, name='reject_industry'),
    path('approve_consumer/<int:user_id>/', views.approve_consumer, name='approve_consumer'),
    path('reject_consumer/<int:user_id>/', views.reject_consumer, name='reject_consumer'),
    path('admin_view_industry/', views.admin_view_industry, name='admin_view_industry'),
    path('admin_view_consumers/', views.admin_view_consumer, name='admin_view_consumer'),



]