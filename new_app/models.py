from django.db import models

# Create your models here.
class Employee(models.Model):
    emp_id = models.IntegerField(primary_key=True)
    emp_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    current_project = models.CharField(max_length=100)
    projects_done = models.IntegerField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    salary = models.FloatField()
    promotion_details = models.TextField()

    def __str__(self):
        return self.emp_name