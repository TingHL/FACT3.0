import logging
import os
import re
import sys
from tempfile import TemporaryDirectory

from helperFunctions.uid import create_uid
from objects.firmware import Firmware

# 可选选项
OPTIONAL_FIELDS = ['tags', 'device_part']
# 必选选项
DROPDOWN_FIELDS = ['device_class', 'vendor', 'device_name', 'device_part']


def create_analysis_task(request):
    # 任务 有一系列的属性 
    # device_name, device_part, device_class,vendor,
    # version,release_date,requested_analysis_systems,tags,
    # file_name,binary,uid, release_date, 
    task = _get_meta_from_request(request)
    if request.files['file']:
        task['file_name'], task['binary'] = get_file_name_and_binary_from_request(request)
    task['uid'] = get_uid_of_analysis_task(task)
    if task['release_date'] == '':
        # set default value if date field is empty
        task['release_date'] = '1970-01-01'
    return task


def get_file_name_and_binary_from_request(request):  # pylint: disable=invalid-name
    try:
        file_name = request.files['file'].filename
    except Exception:
        file_name = 'no name'
    file_binary = get_uploaded_file_binary(request.files['file'])
    return file_name, file_binary


def create_re_analyze_task(request, uid):
    task = _get_meta_from_request(request)
    task['uid'] = uid
    if not task['release_date']:
        task['release_date'] = '1970-01-01'
    return task

# 根据上传页面填写的数据 获取元信息
def _get_meta_from_request(request):
    meta = {
        'device_name': request.form['device_name'],
        'device_part': request.form['device_part'],
        'device_class': request.form['device_class'],
        'vendor': request.form['vendor'],
        'version': request.form['version'],
        'release_date': request.form['release_date'],
        # 选中的功能
        'requested_analysis_systems': request.form.getlist('analysis_systems'),
        'tags': request.form['tags']
    }

    # for i in meta['requested_analysis_systems']:
    #     print('requested_analysis_systems:'+i)

    _get_meta_from_dropdowns(meta, request)

    if 'file_name' in request.form.keys():
        meta['file_name'] = request.form['file_name']
    return meta


def _get_meta_from_dropdowns(meta, request):
    for item in meta.keys():
        if not meta[item] and item in DROPDOWN_FIELDS:
            dd = request.form['{}_dropdown'.format(item)]
            if dd != 'new entry':
                meta[item] = dd


def _get_tag_list(tag_string):
    if tag_string == '':
        return []
    return tag_string.split(',')


def convert_analysis_task_to_fw_obj(analysis_task):
    fw = Firmware(scheduled_analysis=analysis_task['requested_analysis_systems'])
    if 'binary' in analysis_task.keys():
        fw.set_binary(analysis_task['binary'])
        fw.file_name = analysis_task['file_name']
    else:
        if 'file_name' in analysis_task.keys():
            fw.file_name = analysis_task['file_name']
        fw.overwrite_uid(analysis_task['uid'])
    fw.set_device_name(analysis_task['device_name'])
    fw.set_part_name(analysis_task['device_part'])
    fw.set_firmware_version(analysis_task['version'])
    fw.set_device_class(analysis_task['device_class'])
    fw.set_vendor(analysis_task['vendor'])
    fw.set_release_date(analysis_task['release_date'])
    for tag in _get_tag_list(analysis_task['tags']):
        fw.set_tag(tag)
    return fw


def get_uid_of_analysis_task(analysis_task):    
    if analysis_task['binary']:
        # SHA256_SIZE创建文件的唯一uid
        uid = create_uid(analysis_task['binary'])
        return uid
    return None


def get_uploaded_file_binary(request_file):
    if request_file:
        tmp_dir = TemporaryDirectory(prefix='fact_upload_')
        tmp_file_path = os.path.join(tmp_dir.name, 'upload.bin')
        try:
            # 将上传文件保存在tmp_file_path
            request_file.save(tmp_file_path)
            with open(tmp_file_path, 'rb') as tmp_file:
                # 读取上传文件到binary中,返回 (一次性读取到内存中)
                binary = tmp_file.read()
            tmp_dir.cleanup()
            return binary
        except Exception:
            return None
    return None


def check_for_errors(analysis_task):
    error = {}
    for key in analysis_task:
        if analysis_task[key] in [None, '', b''] and key not in OPTIONAL_FIELDS:
            error.update({key: 'Please specify the {}'.format(key.replace('_', ' '))})
    return error


def is_sanitized_entry(entry):
    try:
        if re.search(r'_[0-9a-f]{64}_[0-9]+', entry) is None:
            return False
        return True
    except TypeError:  # DB entry has type other than string (e.g. integer or float)
        return False
    except Exception as e_type:
        logging.error('Could not determine entry sanitization state: {} {}'.format(sys.exc_info()[0].__name__, e_type))
        return False
