import copy
import hashlib, random, binascii
import sys, os
import imghdr
import math
from PIL import Image
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.http import Http404
from django.template import loader

from .models import Uploader
from .forms import UploadFileForm
from .configs import *

uploadDir = os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'static/moebox/files/')
thumbDir = os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'static/moebox/thumb/')
thumbWidth = 200

def deleteFile(object):
    path=uploadDir
    if object.secret:
        path = os.path.join(path,object.secret_key.split('%')[1])
    path=os.path.join(path,str(object.pk)+"."+object.file_ext)
    if os.path.exists(path):
        print("delete file:"+str(object.auto_increment_id))
        os.remove(path)
    if object.secret:
        path = os.path.join(uploadDir,object.secret_key.split('%')[1])
        if os.path.exists(path):
            os.rmdir(path)
    tpath=os.path.join(thumbDir,str(object.pk)+"."+object.file_ext)
    if os.path.exists(tpath):
        print("delete file:"+str(object.auto_increment_id))
        os.remove(tpath)

def allFileSize(path):
    total = 0
    for root, dirs, files in os.walk(path):
        total += sum(os.path.getsize(os.path.join(root, name)) for name in files)
    return total

def calcKey(salt,key):
    return salt + '%' + binascii.hexlify(hashlib.pbkdf2_hmac('sha256',key.encode('utf-8'),salt.encode('utf-8'),100)).decode('utf-8')

def createThumbnail(object):
    spath = os.path.join(uploadDir, str(object.pk)+"."+object.file_ext)
    opath = os.path.join(thumbDir, str(object.pk)+"."+object.file_ext)
    if not os.path.exists(thumbDir):
        os.mkdir(thumbDir)
    if os.path.exists(spath) and imghdr.what(spath):
        image = Image.open(spath)
        w,h = image.size
        if w>h:
            resize_img = image.resize((thumbWidth,math.floor(h*thumbWidth/w)))
        else:
            resize_img = image.resize((math.floor(w*thumbWidth/h),thumbWidth))

        resize_img.save(opath)

def sizeFormat(b):
    if b < 1024:
        return '%i' %b + 'B'
    if b < 1024**2:
        return '%.1f' % float(b/1024) + 'KB'
    if b < 1024**3:
        return '%.1f' % float(b/(1024**2)) + 'MB'
    if b < 1024**4:
        return '%.1f' % float(b/(1024**3)) + 'GB'
    if b < 1024**5:
        return '%.1f' % float(b/(1024**4)) + 'TB'

def index(request):
    return page(request, 1)

def delete(request, request_id):
    object = get_object_or_404(Uploader, auto_increment_id=request_id)
    context = { 
            'object' : copy.copy(object),
            'disp_orgname' : dispOrgname,
            }
    if request.method == 'GET':
        return render(request,'moebox/delete.html', context)
    if object.delete_key == calcKey(object.delete_key.split('%')[0],request.POST['delete_key']) :
        deleteFile(object)
        object.delete()
        return render(request,'moebox/delete_ok.html', context)
    return render(request,'moebox/delete_ng.html', context)

def download(request, request_id):
    object = get_object_or_404(Uploader, auto_increment_id=request_id)
    context = { 
            'object' : object,
            'disp_orgname' : dispOrgname,
            }
    if object.secret:
        if request.method == 'GET':
            return render(request,'moebox/download.html',context)
        try:
            if object.secret_key == calcKey(object.secret_key.split('%')[0],request.POST['secret_key']):
                context['path'] = os.path.join('moebox/files',object.secret_key.split('%')[1],str(object.pk)+"."+object.file_ext)
                return render(request,'moebox/download_ok.html',context)
            return render(request,'moebox/download_ng.html',context)
        except:
            raise Http404("Download Error")
    else:
        context['path'] = os.path.join('moebox/files',str(object.pk)+"."+object.file_ext)
        return render(request,'moebox/download_ok.html',context)

def upload(request):
    if not request.method == 'POST':
            raise Http404("Page Not Found.")
    form = UploadFileForm(request.POST,request.FILES)
    if not form.is_valid():
        raise Http404("form invalid",form)
    file = request.FILES['uploadfile']
    salt = str(random.getrandbits(256))
    context = {
            'original_filename' : file.name,
            'delete_key' : calcKey(salt,request.POST['delete_key']),
            'comment' : request.POST['comment'],
            'file_ext' : file.name.split(".")[len(file.name.split("."))-1],
            }
    if 'secret' in request.POST:
        salt = str(random.getrandbits(256))
        context['secret'] = True
        context['secret_key'] = calcKey(salt,request.POST['secret_key'])
    q = Uploader(**context)
    q.save()
    path = uploadDir
    try:
        if not os.path.exists(path):
            os.mkdir(path)
        if q.secret:
            path = os.path.join(path, q.secret_key.split('%')[1])
            os.mkdir(path)
        path = os.path.join(path, str(q.pk)+"."+q.file_ext)
        with open(path,'wb+') as f:
            for chunk in file.chunks():
                f.write(chunk)
        size = os.path.getsize(path)
        if useMinSize and minSize > size:
            raise Http404("size too small")
        if maxSize < size:
            raise Http404("size too big")
        q.size= sizeFormat(size)
        q.save()
    except Exception as e:
        print(e)
        deleteFile(q)
        q.delete()
        return render(request, 'moebox/upload_ng.html', { 'object' : q })
    if not q.secret:
        createThumbnail(q)

    while Uploader.objects.count() > maxLog:
        deleteFile(Uploader.objects.order_by('auto_increment_id')[0])
        Uploader.objects.order_by('auto_increment_id')[0].delete()

    if useMaxAllSize:
        while allFileSize(uploadDir) > maxAllSize:
            deleteFile(Uploader.objects.order_by('auto_increment_id')[0])
            Uploader.objects.order_by('auto_increment_id')[0].delete()

    return render(request, 'moebox/upload_ok.html', { 'object' : q })

def page(request, page_id):
    page_id = int(page_id or "1")
    page_num = Uploader.objects.count() // pageLog 
    if Uploader.objects.count()%pageLog > 0 :
        page_num += 1

    if int(page_id) > max(1,page_num):
        raise Http404("Page not found.")

    if page_id == 0:
        objects = Uploader.objects.order_by('-auto_increment_id')
    else:
        objects = Uploader.objects.order_by('-auto_increment_id')[pageLog*(page_id-1):pageLog*page_id]

    form = UploadFileForm()
    context = {
            'page_range' : range(1,page_num+1),
            'objects' : objects,
            'form' : form,
            'path' : 'moebox/files/',
            'thumb': 'moebox/thumb/',
            'max_log' : maxLog,
            'max_size' : sizeFormat(maxSize),
            'disp_comment' : dispComment,
            'disp_date' : dispDate,
            'disp_size' : dispSize,
            'disp_orgname' : dispOrgname,
            }
    if useMaxAllSize:
        context['max_all_size'] = sizeFormat(maxAllSize)
    if useMinSize:
        context['min_size'] = sizeFormat(minSize)

    return render(request, 'moebox/index.html', context)

