#！/usr/bin/python
#此句用于指定脚本执行的py版本
# -*- coding: UTF-8 -*-
import time
import tornado.ioloop
import tornado.web
from mysqldb import *
from func import *

class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        # gen.sleep(10)
        self.write("Hello, world")

#登录接口
class login(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        user_name = self.get_argument('user_name')
        password = self.get_argument('password')

        sql = "SELECT id,agent_phone,agent_level_id FROM wz_agent WHERE agent_phone=%s AND agent_password=%s"
        try:
            datas = yield executesql(sql,(user_name,password))
            if not datas:
                return returnJson(self, 0, msg='账号密码错误')
            print(user_name, password, datas)
            token = create_Token(datas[0]['id'], datas[0]['agent_phone'], datas[0]['agent_level_id'])
            endtime = int(time.time()) + 2000  # 截止日期
            adddata = {'user_id': datas[0]['id'], 'token': token, 'expires_in': endtime}
            print(adddata)
            add('wz_token', adddata)
        except:
            return returnJson(self, 0, msg='用户不存在')



        # print(token)
        returnJson(self,1,data={'token':token})

#获取商户列表接口
class getMerchantList(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        agent_id = self.get_argument('agent_id')
        sql = "SELECT id,mer_name from wz_merchant WHERE mer_parent_agent = %s"
        try:
            datas = yield executesql(sql,agent_id)
            if not datas:
                return returnJson(self, 0, msg='该代理还没有商户列表')
        except:
            return returnJson(self, 0, msg='出现异常错误')
        print(datas)
        dic = {'merchant_list':datas}
        return returnJson(self, 1, data=dic)

#获取交易流水接口
class getOrderList(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        user_id = self.get_argument('user_id') #用户ID
        user_type = self.get_argument('user_type') #用户类别 1代理商 2商户
        trans_time = self.get_argument('trans_time') #交易时间 2018-
        order_type = self.get_argument('order_type') #排序方式 1升序，2降序
        if order_type == '1':
            order_type = 'asc'
        else:
            order_type = 'desc'
        if user_type == '2':
            chip_sql = "WHERE merchant_id = %s AND DATE_FORMAT(time,'%%Y-%%m-%%d') = %s order by time {}".format(order_type)
        sql = "SELECT id,order_no from wz_order {} ".format(chip_sql)
        print(sql)
        try:
            datas = yield executesql(sql,(user_id,'2018-04-03'))
            print(datas)
            if not datas:
                return returnJson(self, 0, msg='该代理还没有交易流水记录')
        except:
            return returnJson(self, 0, msg='出现异常错误')
        dic = {'order_list': datas}
        # print(datas)

        return returnJson(self, 1, data=dic)

# 添加商户接口
class addMerchant(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-type', 'x-www-form-urlencoded;charset=utf-8')

    @gen.coroutine
    def post(self):
        data = self.request.arguments
        try:
            datas = yield add('wz_merchant',data)
            print(datas)
            if not datas:
                return returnJson(self, 0, msg='添加失败')
        except:
            print(111)
            return returnJson(self, 0, msg='出现异常错误，请重试')

        dic = {'merchant_info': datas}
        return returnJson(self, 1, data=dic)


# 获取商户资料接口
class getMerchnatInfoById(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Content-type', 'x-www-form-urlencoded;charset=utf-8')

    @gen.coroutine
    def post(self):
        merchant_id = self.get_argument('merchant_id')  # 商户ID

        try:
            where = ["WHERE id = %s",[merchant_id]]
            datas = yield query('wz_merchant','*',where)
            print(datas)
            if not datas:
                return returnJson(self, 0, msg='获取失败，请重试')
        except:
            return returnJson(self, 0, msg='出现异常错误，请重试')

        dic = {'merchant_info': datas}
        return returnJson(self, 1, data=dic)

# 获取商户资料接口
class updateMerchantById(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):
        merchant_id = self.get_argument('merchant_id')  # 商户ID
        merchant_logo = self.get_argument('merchant_logo')  # 商户logo
        merchant_name = self.get_argument('merchant_name')
        # print(merchant_logo)
        try:
            where = ["WHERE id = %s",[merchant_id]]
            res = {'mer_name':merchant_name,'mer_logo': merchant_logo}
            datas = yield update('wz_merchant',res,where)
            # print(datas)
            if not datas:
                return returnJson(self, 0, msg='获取失败，请重试')
        except:
            return returnJson(self, 0, msg='出现异常错误，请重试')

        dic = {'merchant_info': datas}
        return returnJson(self, 1, data=dic)

# 获取商户资料接口
class resetPassword(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):

        userid = self.get_argument('userid')  # 用户ID
        phone = self.get_argument('phone')  # 手机号
        # old_password = self.get_argument('old_password') #原密码
        new_password = self.get_argument('new_password')  #新密码
        try:
            where = ["WHERE id = %s and agent_phone = %s",[userid,phone]]
            res = {'agent_password':new_password}
            datas = yield update('wz_agent',res,where)
            # print(datas)
            if not datas:
                return returnJson(self, 0, msg='获取失败，请重试')
        except:
            return returnJson(self, 0, msg='出现异常错误，请重试')

        dic = {'merchant_info': datas}
        return returnJson(self, 1, data=dic)

# 获取商户资料接口
class countMoneyById(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):

        agent_id = self.get_argument('agent_id')  # 代理商ID
        startDate = self.get_argument('startDate')  # 起时间
        endDate = self.get_argument('endDate')   # 终时间

        try:
            where = ["WHERE agent_id = %s and (time > %s and time < %s)",[agent_id,startDate,endDate]]
            datas = yield query('wz_agent_profit','*',where)
            if not datas:
                return returnJson(self, 0, msg='获取失败，请重试')
        except:
            return returnJson(self, 0, msg='出现异常错误，请重试')

        dic = {'merchant_info': datas}
        return returnJson(self, 1, data=dic)

# 获取提现记录接口
class getTradeHistory(tornado.web.RequestHandler):
    @gen.coroutine
    def post(self):

        agent_id = self.get_argument('agent_id')  # 代理商ID
        trade_type = self.get_argument('trade_type')  # 交易类型(昝定义 1正在提现  2提现完成)
        startDate = self.get_argument('startDate')  # 起时间
        endDate = self.get_argument('endDate')   # 终时间

        try:
            where = ["WHERE agent_id = %s and status = %s and (pub_time > %s and pub_time < %s)",[agent_id,trade_type,startDate,endDate]]
            datas = yield query('wz_agent_tx','*',where)
            if not datas:
                return returnJson(self, 0, msg='获取失败，请重试')
        except:
            return returnJson(self, 0, msg='出现异常错误，请重试')

        dic = {'merchant_info': datas}
        return returnJson(self, 1, data=dic)

application = tornado.web.Application([

    (r"/getTradeHistory", getTradeHistory),
    (r"/countMoneyById", countMoneyById),
    (r"/resetPassword", resetPassword),
    (r"/updateMerchantById", updateMerchantById),
    (r"/getMerchnatInfoById", getMerchnatInfoById),
    (r"/addMerchant", addMerchant),
    (r"/getOrderList", getOrderList),
    (r"/getMerchantList", getMerchantList),
    (r"/login", login),
    (r"/", MainHandler),
])
application.add_handlers(r"^(www/.)?a/.com$", [(r"/", MainHandler)])
if __name__ == "__main__":
    application.listen(8000)
    # application.listen(8001)
    # application.listen(8002)
    # application.listen(8003)
    tornado.ioloop.IOLoop.instance().start()