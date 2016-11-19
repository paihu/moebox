from django.db import models

# Create your models here.


class Uploader(models.Model):
    auto_increment_id = models.AutoField(primary_key=True)
    original_filename = models.CharField(max_length=1024)
    secret = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=1024, null=True)
    file_ext = models.CharField(max_length=10)
    delete_key = models.CharField(max_length=1024)
    comment = models.CharField(max_length=1024, null=True)
    upload_date = models.DateTimeField(auto_now=True)
    size = models.CharField(max_length=8)
    thumbnail = models.BooleanField(blank=True,default=False)

    def __str__(self):
        return str(self.auto_increment_id)
