# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import json
import requests
import time
import sys
import os
from werkzeug.utils import secure_filename
import dingtalk.api

server = Flask(__name__)

token = {}
file_name = os.path.dirname(__file__) + '/message_plus.json'
# 临时文件目录
temp_folder = os.path.dirname(__file__) + '/temp/'

if not os.path.exists(temp_folder):
    print(temp_folder, "not exists ,exec makedirs")
    os.makedirs(temp_folder)

send_message_url = "https://oapi.dingtalk.com/message/send_to_conversation"
get_token_url = "https://oapi.dingtalk.com/gettoken"
get_user_info_url = "https://oapi.dingtalk.com/topapi/v2/user/getuserinfo"
media_upload_url = "https://oapi.dingtalk.com/media/upload"


class ResponseEntity:
    # 0:success
    errcode = 0
    errmsg = "ok"
    time = time.time()

    def __init__(self):
        pass

    # def __init__(self, errcode, errmsg):
    #     self.errcode = errcode
    #     self.errmsg = errmsg

    def none_args(self):
        self.errcode = -1
        self.errmsg = '请求参数为空'
        return self.to_dic()

    def error_500(self):
        self.errcode = 500
        self.errmsg = '服务器端内部错误'
        return self.to_dic()

    def error_file_size_limited(self):
        self.errcode = 400
        self.errmsg = '文件不能超过1M,请重新上传'
        return self.to_dic()

    def error_file_type(self):
        self.errcode = 400
        self.errmsg = '文件类型错误,请重新上传'
        return self.to_dic()

    def to_dic(self):
        return {
            "errcode": self.errcode,
            "errmsg": self.errmsg,
            "time": self.time,
        }



@server.route("/gettoken", methods=["GET"])
def gettoken():

    if request.args is None:
        return json.dumps(ResponseEntity().none_args(), ensure_ascii=False)

    get_data = request.args.to_dict()
    result = inner_get_token(get_data)
    result_entity = result.json()
    result_entity['time'] = time.time()
    return jsonify(result_entity)


def inner_get_token(params_data):
    result = requests.get(get_token_url, params_data)
    return result


def get_token_from_config():
    global token
    with open(file_name) as f:
        data = json.load(f)
    params_data = {'appkey': data['appkey'], 'appsecret': data['appsecret']}
    token_result = inner_get_token(params_data)
    if token_result.json()['errcode'] == 0:
        token = token_result.json()
        token['time'] = time.time()
    return token


@server.route('/message/send_to_conversation', methods=['POST'])
def send_to_conversation():
    global token
    if request.json is None:
        return json.dumps(ResponseEntity().none_args(), ensure_ascii=False)
    url = send_message_url
    result_entity = is_refresh_token(url, request.get_data())
    return result_entity


@server.route("/user/getuserinfo", methods=['POST', 'GET'])
def get_user_info():
    global token
    url = get_user_info_url

    if request.args is None and request.args["code"] is None:
        return json.dumps(ResponseEntity().none_args(), ensure_ascii=False)
    result_entity = is_refresh_token(url, request.args.to_dict())
    return result_entity


def is_refresh_token(url, data):
    no_access_token = len(request.args) == 0 or request.args.get('access_token') is None
    if no_access_token:
        if len(token) != 0 and (float(token['time']) + float(token['expires_in']) > time.time()):
            pass
        else:
            get_token_from_config()
        url += "?access_token=" + token['access_token']
    else:
        url += "?access_token=" + request.args['access_token']
    result = requests.post(url, data)
    result_entity = result.json()
    # token 失效重试1次
    if no_access_token and result_entity['errcode'] == 40014:
        token.clear()
        get_token_from_config()
        url = send_message_url + "?access_token=" + token["access_token"]
        result = requests.post(url, request.get_data())
        result_entity = result.json()
    return result_entity


def get_access_token():
    if len(token) != 0 and (float(token['time']) + float(token['expires_in']) > time.time()):
        return token["access_token"]
    else:
        return get_token_from_config()["access_token"]


@server.route('/media/upload', methods=['POST'])
def media_upload():
    """
        上传媒体文件 https://developers.dingtalk.com/document/app/upload-media-files?#topic-1936786
        :param file 文件域 限制最大1M , https://developers.dingtalk.com/document/app/upload-media-files
    """
    upload_file = request.files['file']
    content_length = request.content_length
    if upload_file is None:
        return ResponseEntity().none_args()
    # 最大1M, 其他请求头: 300
    if content_length > 1048576+300:
        return ResponseEntity().error_file_size_limited()

    print("media_upload: file:", upload_file)
    base_path = temp_folder
    file_name = secure_filename(upload_file.filename)
    file_type = upload_file.content_type.split("/")[0]

    if file_type.upper() != "IMAGE":
        return ResponseEntity().error_file_type()

    upload_path = os.path.join(base_path, file_name)
    upload_file.save(upload_path)
    #表单内容
    # form_data = request.form

    # 开始上传文件
    no_access_token = len(request.args) == 0 or request.args.get('access_token') is None
    access_token = request.args.get('access_token') if not no_access_token else get_access_token()
    result = inner_upload_file(access_token, file_name, upload_path, file_type)

    if result["errcode"] == 0:
        # 删除临时文件
        os.remove(upload_path)
    return result


def inner_upload_file(access_token, file_name, file_path, file_type):
    req = dingtalk.api.OapiMediaUploadRequest(media_upload_url)
    req.type = file_type
    req.media = dingtalk.api.FileItem(file_name, open(file_path, 'rb'))
    try:
        resp = req.getResponse(access_token)
        print("inner_upload_file url:", media_upload_url, ", access_token:", access_token, ", resp:", resp)
        return resp
    except Exception as e:
        print(e)
    return ResponseEntity().error_500()


if __name__ == '__main__':
    # 第一个变量为配置文件
    print(sys.argv)
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    server.run(debug=True)
