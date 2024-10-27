from django.conf.urls.static import static
from django.urls import path

from Cottage import settings
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
    path('view_industry', views.view_industry, name='view_industry'),
    path('admin_view_industry', views.admin_view_industry, name='admin_view_industry'),
    path('admin_view_consumer', views.admin_view_consumer, name='admin_view_consumer'),
    path('consumer_view_industry/', views.consumer_view_industry, name='consumer_view_industry'),
    path('consumer_view_products', views.consumer_view_products, name='consumer_view_products'),
    path('purchase/<int:product_id>/', views.purchase_product, name='purchase_product'),
    path('purchase/<int:product_id>/consumer/consumer_purchase_confirm/', views.consumer_purchase_confirm, name='consumer_purchase_confirm'),
    path('view_consumer', views.view_consumer, name='view_consumer'),
    path('submit_complaint/', views.submit_complaint, name='submit_complaint'),
    path('view_complaints/', views.view_complaints, name='view_complaints'),
    path('complaint/<int:complaint_id>/', views.view_complaint_detail, name='view_complaint_detail'),
    path('admin_view_complaints/', views.admin_view_complaints, name='admin_view_complaints'),  # Admin complaints view
    path('admin_view_complaint_detail/<int:complaint_id>/', views.admin_view_complaint_detail, name='admin_view_complaint_detail'),
    # Admin complaint detail
    path('add_industry', views.add_industry, name='add_industry'),
    path("update_industry/<int:id>/", views.update_industry, name="update_industry"),
    path('delete_industry/<int:id>/', views.delete_industry, name='delete_industry'),

    path('approve_industry/<int:user_id>/', views.approve_industry, name='approve_industry'),
    path('reject_industry/<int:user_id>/', views.reject_industry, name='reject_industry'),

    path('admin_view_industry/', views.admin_view_industry, name='admin_view_industry'),
    path('admin_view_consumers/', views.admin_view_consumer, name='admin_view_consumer'),



    path('industry_notifications/', views.industry_notifications, name='industry_notifications'),
    path('consumer_notifications/', views.consumer_notifications, name='consumer_notifications'),
    path('add_notifications', views.add_notifications, name='add_notifications'),
    path('admin_view_notifications', views.admin_view_notifications, name='admin_view_notifications'),

    path("feedback", views.feedback, name="feedback"),
    path("view", views.view, name="view"),
    path('feedbacks', views.feedbacks, name='feedbacks'),
    path("reply_feedback/<int:id>/", views.reply_feedback, name="reply_feedback"),
    path('add_product', views.add_product, name='add_product'),

    path('profile/<int:id>', views.profile, name='profile'),
    path('product_list', views.product_list, name='product_list'),
    path("update_product/<int:id>/", views.update_product, name="update_product"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)