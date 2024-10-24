from django.contrib import admin
from new_app import models
from new_app.models import Notification, NotificationAdmin

# Define the FeedbackAdmin class before using it
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'description', 'rating')

# Register the models with the admin interface
admin.site.register(models.Login)
admin.site.register(models.IndustryRegister)
admin.site.register(models.ConsumerRegister)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(models.Feedback, FeedbackAdmin)  # FeedbackAdmin is now defined
admin.site.register(models.IndustryProfile)
admin.site.register(models.Product)
admin.site.register(models.Purchase)
admin.site.register(models.Order)

