from django.contrib import admin

from new_app import models

admin.site.register(models.Login)
admin.site.register(models.IndustryRegister)
admin.site.register(models.ConsumerRegister)
