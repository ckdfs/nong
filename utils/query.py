from pymysql import *
import pandas as pd
from sqlalchemy import create_engine
import time


def querys(sql, params, type='no_select'):
    conn = connect(host='localhost', user='root', password='root', database='nong', port=3306)
    cursor = conn.cursor()
    params = tuple(params)
    cursor.execute(sql, params)
    if type != 'no_select':
        data_list = cursor.fetchall()
        conn.commit()
        conn.close()
        return data_list
    else:
        conn.commit()
        conn.close()
        return '数据库语句执行成功'


def read_sql():
    # conn = connect(host='localhost', user='root', password='root', database='nong', port=3306)
    # sql = "select * from data"
    # df = pd.read_sql_query(sql, conn)
    # 关闭连接
    # conn.close()
    engine = create_engine("mysql+pymysql://root:root@localhost:3306/nong")
    sql = '''select * from data'''
    df = pd.read_sql(sql, engine)
    return df


def gettime():
    time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return time1


# MySQL保存
def sqlsave(jd):
    try:
        querys(
            "INSERT INTO data (time,id,wendu,shidu,guang,qiya,kongqi,turang,yushui,yanwu) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            [gettime(), jd['id'], jd['wendu'], jd['shidu'], jd['guang'], jd['qiya'], jd['kongqi'], jd['turang'], jd['yushui'], jd['yanwu']])
        print("%s 数据库保存成功！" % gettime())
    except:
        pass
