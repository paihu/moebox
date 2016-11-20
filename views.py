import copy
import hashlib
import random
import binascii
import sys
import os
import imghdr
import math
from pgmagick import Image, FilterTypes

from django.apps import apps
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.http import Http404
from django.template import loader

from .models import Uploader
from .forms import UploadFileForm

settings = apps.get_app_config('moebox')

def _filename_format(name, ext):
    return settings.file_pre + str(name) + "." + ext


def _delete_file(object):
    path = settings.src_dir
    if object.secret:
        path = os.path.join(path, object.secret_key.split('%')[1])
    path = os.path.join(path, _filename_format(
        object.auto_increment_id, object.file_ext))
    if os.path.exists(path):
        print("delete file:" + str(object.auto_increment_id))
        os.remove(path)
    if object.secret:
        path = os.path.join(settings.src_dir, object.secret_key.split('%')[1])
        if os.path.exists(path):
            os.rmdir(path)
    tpath = os.path.join(settings.thumb_dir, _filename_format(
        object.auto_increment_id, object.file_ext))
    if os.path.exists(tpath):
        print("delete file:" + str(object.auto_increment_id))
        os.remove(tpath)


def _all_file_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        total += sum(os.path.getsize(os.path.join(root, name))
                     for name in files)
    return total


def _calc_key(salt, key):
    return salt + '%' + binascii.hexlify(hashlib.pbkdf2_hmac('sha256', key.encode('utf-8'), salt.encode('utf-8'), 100)).decode('utf-8')


def _create_thumbnail(object):
    spath = os.path.join(settings.src_dir, _filename_format(
        object.auto_increment_id, object.file_ext))
    opath = os.path.join(settings.thumb_dir, _filename_format(
        object.auto_increment_id, object.file_ext))
    if not os.path.exists(settings.thumb_dir):
        os.mkdir(settings.thumb_dir)
    if os.path.exists(spath) and imghdr.what(spath):
        image = Image(spath)
        if image.columns() > image.rows():
            scale = math.floor(100 * settings.thumb_width / image.columns())
        else:
            scale = math.floor(100 * settings.thumb_width / image.rows())

        image.scale(str(scale)+"%")
        image.write(opath)
        return True
    return False

def _size_format(b):
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


def index(request):
    return page(request, 1)


def delete(request, request_id):
    object = get_object_or_404(Uploader, auto_increment_id=request_id)
    context = {
        'object': copy.copy(object),
        'disp_orgname': settings.disp_orgname,
    }
    if request.method == 'GET':
        return render(request, 'moebox/delete.html', context)
    if object.delete_key == _calc_key(object.delete_key.split('%')[0], request.POST['delete_key']):
        _delete_file(object)
        object.delete()
        return render(request, 'moebox/delete_ok.html', context)
    return render(request, 'moebox/delete_ng.html', context)


def download(request, request_id):
    object = get_object_or_404(Uploader, auto_increment_id=request_id)
    context = {
        'object': object,
        'disp_orgname': settings.disp_orgname,
    }
    if object.secret:
        if request.method == 'GET':
            return render(request, 'moebox/download.html', context)
        try:
            if object.secret_key == _calc_key(object.secret_key.split('%')[0], request.POST['secret_key']):
                context['path'] = os.path.join('moebox/files', object.secret_key.split(
                    '%')[1], _filename_format(object.auto_increment_id, object.file_ext))
                return render(request, 'moebox/download_ok.html', context)
            return render(request, 'moebox/download_ng.html', context)
        except:
            raise Http404("Download Error")
    else:
        context['path'] = os.path.join(
            'moebox/files', _filename_format(object.auto_increment_id, object.file_ext))
        return render(request, 'moebox/download_ok.html', context)


def upload(request):
    if not request.method == 'POST':
        raise Http404("Page Not Found.")
    form = UploadFileForm(request.POST, request.FILES)
    if not form.is_valid():
        return HttpResponse("Invalid data: %s" % form,status=400)
    file = request.FILES['uploadfile']
    salt = str(random.getrandbits(256))
    context = {
        'original_filename': file.name,
        'delete_key': _calc_key(salt, request.POST['delete_key']),
        'comment': request.POST['comment'],
        'file_ext': file.name.split(".")[len(file.name.split(".")) - 1],
    }
    if context['file_ext'] in settings.deny_ext.split(','):
        return HttpResponse("the file is not upload: %s" % file.name,status=400)
    if not context['file_ext'] in settings.up_ext.split(','):
        if not settings.up_all:
            return HttpResponse("the file is not upload: %s" % file.name,status=400)
        if not settings.ext_org:
            context['file_ext'] = settings.ext_all
    if settings.min_flag and settings.min_size > file.size:
        return HttpResponse("size too small: %d>%d" % (settings.min_size,file.size),status=400)
    if settings.max_size < file.size:
        return HttpResponse("size too big: %d<%d" % (settings.max_size,file).size,status=400)

    if 'secret' in request.POST:
        salt = str(random.getrandbits(256))
        context['secret'] = True
        context['secret_key'] = _calc_key(salt, request.POST['secret_key'])
    q = Uploader(**context)
    q.save()
    path = settings.src_dir
    try:
        if not os.path.exists(path):
            os.mkdir(path)
        if q.secret:
            path = os.path.join(path, q.secret_key.split('%')[1])
            os.mkdir(path)
        path = os.path.join(path, _filename_format(
            str(q.auto_increment_id), context['file_ext']))
        with open(path, 'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)
        size = os.path.getsize(path)
        q.size = _size_format(size)
        q.save()
    except Exception as e:
        print(e)
        _delete_file(q)
        q.delete()
        return render(request, 'moebox/upload_ng.html', {'object': q})
    if not q.secret:
        q.thumbnail = _create_thumbnail(q)
        q.save()

    while Uploader.objects.count() > settings.max_log:
        _delete_file(Uploader.objects.order_by('auto_increment_id')[0])
        Uploader.objects.order_by('auto_increment_id')[0].delete()

    if settings.max_all_flag:
        while _all_file_size(settings.src_dir) > settings.max_all_size:
            _delete_file(Uploader.objects.order_by('auto_increment_id')[0])
            Uploader.objects.order_by('auto_increment_id')[0].delete()

    return render(request, 'moebox/upload_ok.html', {'object': q})


def page(request, page_id):
    page_id = int(page_id or "1")
    page_num = Uploader.objects.count() // settings.page_log
    if Uploader.objects.count() % settings.page_log > 0:
        page_num += 1

    if int(page_id) > max(1, page_num):
        raise Http404("Page not found.")

    if page_id == 0:
        objects = Uploader.objects.order_by('-auto_increment_id')
    else:
        objects = Uploader.objects.order_by(
            '-auto_increment_id')[settings.page_log * (page_id - 1):settings.page_log * page_id]

    form = UploadFileForm()
    context = {
        'page_range': range(1, page_num + 1),
        'objects': objects,
        'form': form,
        'path': settings.http_src_path,
        'thumb': settings.http_thumb_dir,
        'max_log': settings.max_log,
        'max_size': _size_format(settings.max_size),
        'disp_comment': settings.disp_comment,
        'disp_date': settings.disp_date,
        'disp_size': settings.disp_size,
        'disp_orgname': settings.disp_orgname,
        'file_prefix': settings.file_pre,
    }
    if settings.max_all_flag:
        context['max_all_size'] = _size_format(settings.max_all_size)
    if settings.min_flag:
        context['min_size'] = _size_format(settings.min_size)

    return render(request, 'moebox/index.html', context)
