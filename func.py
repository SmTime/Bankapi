#！/usr/bin/python
#此句用于指定脚本执行的py版本
# -*- coding: utf-8 -*-
#此句用于让python脚本能够识别一些字符，如汉字
import hashlib
import json

from urllib import parse
import uuid

from datetime import datetime
import json

from decimal import Decimal


class DateEncoder(json.JSONEncoder):
    # def _iterencode(self, o, markers=None):
    #
    #     return super(DecimalEncoder, self)._iterencode(o, markers)

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.__str__()
        if isinstance(obj, Decimal):
            return obj.__str__()
        return json.JSONEncoder.default(self, obj)

def returnJson(self,code,msg='success',data=''):
    resp = {'code': code, 'msg': msg, 'data': data}
    self.write(json.dumps(resp, indent=4, separators=(',', ':'), cls=DateEncoder))
    self.finish()

def create_md5(code = str(uuid.uuid1())):   #通过MD5的方式创建
    m = hashlib.md5()
    m.update(code.encode(encoding='utf-8'))
    return m.hexdigest()

def create_Token(id,user_name,role_id):
    # 用户 id
    # 账号 user_name
    # 角色类型 role_id
    # 32位随机字符串 nonce_str
    nonce_str = create_md5()[0:16]
    # “id = 10086 & user_name = 15871365175 & role_id = 1 & nonce_str = ibuaiVcKdpRxkhJA”
    d = {'id': id, 'username': user_name, 'role_id': role_id, 'nonce_str': nonce_str}
    string1 = parse.urlencode(d)
    return create_md5(string1).upper()


def create_Sign(dic,timestamp,Token):
    sortdic = sorted(dic.items(), key=lambda d: d[0], reverse=False) #按照字典序排序后
    string1 = parse.urlencode(sortdic)
    string2 = string1 + str(timestamp)#加上前端传输的时间戳
    stringSignTemp = string2 + Token #最后拼接上会话Token
    return create_md5(stringSignTemp).upper()