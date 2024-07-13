from django.db import models


# Create your models here.
class Upload(models.Model):
    file_data = models.FileField(null=True, blank=False, upload_to="media/%Y/%m/%d/")
    date_uploaded = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        db_table = "upload"
        ordering = ["id"]
