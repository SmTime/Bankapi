#！/usr/bin/python
#此句用于指定脚本执行的py版本
# -*- coding: utf-8 -*-
#此句用于让python脚本能够识别一些字符，如汉字
import tormysql
from tornado import gen

pool = tormysql.ConnectionPool(
    max_connections=20,  # max open connections
    idle_seconds=7200,  # conntion idle timeout time, 0 is not timeout
    wait_connection_timeout=3,  # wait connection timeout
    host="127.0.0.1",
    user="root",
    passwd="nnxxx",
    db="wz",
    charset="utf8"
)
@gen.coroutine
def executesql(sql,params):
    with (yield pool.Connection()) as conn:
        with conn.cursor(cursor_cls=tormysql.cursor.DictCursor) as cursor:
            yield cursor.execute(sql,params)
            datas = cursor.fetchall()
            # cursor.close()
            # pool.close()
            raise gen.Return(datas)



@gen.coroutine
def query(table,cols,where=[]):
    cols = ",".join(cols)
    with (yield pool.Connection()) as conn:
        with conn.cursor(cursor_cls=tormysql.cursor.DictCursor) as cursor:
            if where:
                sql = "SELECT {} FROM {} {}".format(cols,table,where[0])
                yield cursor.execute(sql,where[1])
            else:
                sql = "SELECT {} FROM {}".format(cols, table)
                yield cursor.execute(sql)

            datas = cursor.fetchall()
            print(datas)
            # cursor.close()
            # pool.close()
            raise gen.Return(datas)

@gen.coroutine
def add(table,data):
    # 传入一个要添加的data字典,字典的键必须对应列名,
    # 传入一个表名
    strv = []
    length = len(data.items())
    strk = data.keys()

    for k, v in data.items():
        if isinstance(v, list):
            for dv in data[k]:
                data[k] = dv.decode()
        strv.append(data[k])

    strk = ",".join(strk)
    # return returnJson(self, 0, msg=strv)

    # print(strk,strv)
    seat = ('%s,' * length).rstrip(',')
    # print(seat)
    sql = """INSERT INTO {}({}) VALUES({})""".format(table,strk, seat)
    print(sql)
    with (yield pool.Connection()) as conn:
        try:
            with conn.cursor(cursor_cls=tormysql.cursor.DictCursor) as cursor:
                yield cursor.execute(sql,strv)
        except:
            yield conn.rollback()
        else:
            yield conn.commit()

        new_id = cursor.lastrowid
        # pool.close()
        raise gen.Return(new_id)

@gen.coroutine
def update(table,data,where=[]):
    # 传入一个要添加的data字典,字典的键必须对应列名,
    # 传入一个表名
    strv = []
    strk = ''

    for k, v in data.items():
        strk = strk + "{}=%s,".format(k)
        if isinstance(v, list):
            for dv in data[k]:
                data[k] = dv.decode()
        strv.append(data[k])
    strk = strk.strip(',')
    # print(strk)
    with (yield pool.Connection()) as conn:
        try:
            with conn.cursor(cursor_cls=tormysql.cursor.DictCursor) as cursor:
                if where:
                    sql = "UPDATE {} SET {} {}".format(table,strk,where[0])
                    # print(sql)
                    param = strv+where[1]
                    # print(param)
                    yield cursor.execute(sql,param)
                else:
                    sql = "UPDATE {} SET {}".format(table,strk)
                    yield cursor.execute(sql)
        except:
            yield conn.rollback()
        else:
            yield conn.commit()
        datas = cursor.rowcount
        # print(datas)
        # cursor.close()
        # pool.close()
        raise gen.Return(datas)