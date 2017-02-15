from django.core.urlresolvers import reverse
from django.test import TestCase
from .models import Uploader
from .forms import UploadFileForm

# Create your tests here.

class TestUpload(TestCase):
    def test_upload(self):
        self.fail("invalid test case.")

class TestDelete(TestCase):
    def test_delete(self):
        Uploader.objects.create(
                original_filename="test1.txt",file_ext="txt",
                delete_key="1234",comment="test case1")
        res = self.client.get(reverse('delete',args=(1,)))
        self.assertTemplateUsed(res,'moebox/delete.html')
        self.assertContains(res,'No.1')
        self.assertContains(res,'test1.txt')
        self.assertContains(res,'を削除します。')


class TestDownload(TestCase):
    def test_download(self):
        self.fail("invalid test case.")

class TestUpload(TestCase):
    def test_upload(self):
        self.fail("invalid test case.")
