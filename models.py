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
    size = models.IntegerField(null=True)
    thumbnail = models.BooleanField(blank=True,default=False)

    def __str__(self):
        return str(self.auto_increment_id)

    def size_format(self):
        return self._size_format(self.size)

    def _size_format(self, b):
        if b < 1024:
            return '%i' % b + 'B'
        if b < 1024**2:
            return '%.1f' % float(b / 1024) + 'KB'
        if b < 1024**3:
            return '%.1f' % float(b / (1024**2)) + 'MB'
        if b < 1024**4:
            return '%.1f' % float(b / (1024**3)) + 'GB'
        if b < 1024**5:
            return '%.1f' % float(b / (1024**4)) + 'TB'

