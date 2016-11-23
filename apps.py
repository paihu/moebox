from django.apps import AppConfig


class MoeboxConfig(AppConfig):
    name = 'moebox'
    max_log = 300
    max_size = 5000 * 1024 * 1024
    min_flag = True
    min_size = 100 * 1024
    max_all_flag = True
    max_all_size = 5000 * 24 * 1024 * 1024
    file_pre = 'moebox'
    page_log = 20
    thumb_flag = True
    thumb_width = 200
    char_delname = 'D'

    title = 'Uploader'
    up_ext = 'txt,lzh,zip,rar,mp3,avi,mp4,jpg,gif,png'
    up_all = True
    ext_org = False
    ext_all = 'xxx'
    deny_ext = 'php,rb,sh,bat,dll,py,exe'
    change_ext = 'cgi->txt,pl->txt,log->txt,jpeg->jpg,mpeg->mpg'

    home_url = ''
    html_all = True

    disp_comment = True
    disp_date = True
    disp_size = True
    disp_orgname = True

    src_dir = "d:/mydocument/work/django-test/hello/moebox/files/"
    http_src_path = "/moebox/files/"

    thumb_dir = "d:/mydocument/work/django-test/hello/moebox/thumb/"
    http_thumb_dir = "/moebox/thumb/"

    use_modal = True
