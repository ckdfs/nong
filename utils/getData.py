import numpy as np
import pandas as pd
import datetime
import time


def get_date():  # 获取当前日期
    date_str = time.strftime("%Y/%m/%d")
    return date_str


def get_time():  # 获取当前时间
    time_str = time.strftime("%X")
    return time_str


def alive(df):
    # time_now = datetime.datetime.now()
    time_now = datetime.datetime.strptime("2022-11-22 16:17:25", '%Y-%m-%d %H:%M:%S')
    df['timestamp'] = pd.to_datetime(df['time'])
    df['timestamp'] = (time_now - df['timestamp']) / np.timedelta64(1, 's')
    df = df.drop(df[df['timestamp'] > 60].index)
    df = df.drop(labels='timestamp', axis=1)
    return df


def get_device_data(df):
    df = alive(df)
    return df['id'].nunique(), df['id'].unique()


def get_alarm(df):
    df = alive(df)
    df.drop_duplicates(subset=['id'], keep='last', inplace=True)
    # return (df['wendu'] > 40).sum() + (df['shidu'] < 81).sum() + (df['guang'] > 1022).sum() + (df['qiya'] < 985).sum()\
    #     + (df['kongqi'] > 50).sum() + (df['turang'] < 70).sum() + (df['yushui'] < 1).sum() + (df['yanwu'] > 40).sum()
    df['wendu'] = df['wendu'] > 40
    df['shidu'] = df['shidu'] < 81
    df['guang'] = df['guang'] > 1022
    df['qiya'] = df['qiya'] < 985
    df['kongqi'] = df['kongqi'] > 50
    df['turang'] = df['turang'] < 70
    df['yushui'] = df['yushui'] < 1
    df['yanwu'] = df['yanwu'] > 40
    return df


def get_alarm_num(df):  # 获取当前警报数
    df = get_alarm(df)
    return df[df.columns[2:10]].sum().sum()
