from django.contrib import admin
from new_app import models

# Define the FeedbackAdmin class before using it
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'description', 'rating')

# Register the models with the admin interface
admin.site.register(models.Login)
admin.site.register(models.IndustryRegister)
admin.site.register(models.ApprovedIndustryByAdmin)

admin.site.register(models.IndustryProfile)
admin.site.register(models.ConsumerRegister)
admin.site.register(models.Feedback, FeedbackAdmin)  # FeedbackAdmin is now defined
admin.site.register(models.Product)
admin.site.register(models.Purchase)
admin.site.register(models.Order)
admin.site.register(models.Complaint)
admin.site.register(models.ComplaintResponse)

