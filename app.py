from flask import Flask, render_template, request, session, redirect
from flask_mqtt import Mqtt
import numpy as np
import json
import re

from utils import query
from utils import getData

app = Flask(__name__)
app.secret_key = 'nongpi'

app.config['MQTT_BROKER_URL'] = '101.43.164.154'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = 'admin'  # 当你需要验证用户名和密码时，请设置该项
app.config['MQTT_PASSWORD'] = 'zhangxinke233'  # 当你需要验证用户名和密码时，请设置该项
app.config['MQTT_KEEPALIVE'] = 5  # 设置心跳时间，单位为秒
app.config['MQTT_CLIENT_ID'] = 'something'
topic = 'test'

mqtt_client = Mqtt(app)


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected successfully')
        mqtt_client.subscribe(topic)
    else:
        print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    print("client: ", client)
    jsondata = json.loads(message.payload)
    print("msg payload", jsondata)
    query.sqlsave(jsondata)


@app.route('/')
def all_request():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        request.form = dict(request.form)

        def filter_fn(item):
            return request.form['email'] in item and request.form['password'] in item

        users = query.querys('select * from user', [], 'select')
        filter_user = list(filter(filter_fn, users))

        if len(filter_user):
            session['email'] = request.form['email']
            return redirect('/home')
        else:
            return render_template('error.html', message='邮箱或密码错误')


@app.route('/loginOut')
def login_out():
    session.clear()
    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        request.form = dict(request.form)
        print(request.form)
        if request.form['password'] != request.form['passwordChecked']:
            return render_template("error.html", message="两次密码不匹配")

        def filter_fn(item):
            return request.form['email'] in item

        users = query.querys('select * from user', [], 'select')
        filter_list = list(filter(filter_fn, users))
        if len(filter_list):
            return render_template('error.html', message='该用户已被注册')
        else:
            query.querys('insert into user(email,password) values(%s,%s)',
                         [request.form['email'], request.form['password']])
            return redirect('/login')


@app.route('/home', methods=['GET', 'POST'])
def home():
    email = session.get('email')
    df = query.read_sql()
    device_num, device_data = getData.get_device_data(df)
    return render_template(
        'index.html',
        email=email,
        devicenum=device_num,
        device_id=device_data.tolist(),
    )


@app.route('/system_chart_refresh', methods=['GET', 'POST'])
def system_chart_refresh():
    df = query.read_sql()
    device_num, device_data = getData.get_device_data(df)
    timenow = query.gettime()
    num = getData.get_alarm_num(df)
    return [[timenow, device_num],
            [timenow, device_num*8],
            [timenow, int(num)]]


@app.route('/tables', methods=['GET', 'POST'])
def tables():
    email = session.get('email')
    df = query.read_sql()
    device_num, device_data = getData.get_device_data(df)
    return render_template(
        'tables.html',
        email=email,
        devicenum=device_num,
        device_id=device_data.tolist(),
        sqldata=df,
    )


@app.route('/table_refresh')
def table_refresh():
    df = query.read_sql()
    X = np.array(df).tolist()
    # print(df)
    return X


@app.route('/date')
def get_date():
    return getData.get_date()


@app.route('/time')
def get_time():
    return getData.get_time()


@app.route('/device')
def get_device():
    df = query.read_sql()
    device_num, device_data = getData.get_device_data(df)
    return str(device_num)


@app.route('/alarm')
def get_alarm():
    df = query.read_sql()
    num = getData.get_alarm_num(df)
    return str(num)


@app.route('/device_card_refresh')
def device_card_refresh():
    df = query.read_sql()
    device_num, device_data = getData.get_device_data(df)
    return [device_num, device_data.tolist()]


@app.route('/devicepage/<int:deviceid>')
def devicepage(deviceid, methods=['GET', 'POST']):
    email = session.get('email')
    df = query.read_sql()
    device_num, device_data = getData.get_device_data(df)
    return render_template(
        'devicepage.html',
        email=email,
        deviceid=deviceid,
        devicenum=device_num,
        device_id=device_data.tolist(),
    )


@app.route('/device_chart_refresh/<string:id>')
def device_chart_refresh(id):
    df = query.read_sql()
    df = getData.alive(df)
    df = df[df['id'] == id]
    na = np.array(df).tolist()
    k = []
    for i in range(2, 10):
        p = []
        for j in na:
            p = p + [[j[0], j[i]]]
        k = k + [p]
    return k


@app.route('/alarm_svg_refresh/<string:id>')
def alarm_svg_refresh(id):
    df = query.read_sql()
    df = getData.get_alarm(df)
    return np.array(df.loc[df['id'] == id]).tolist()[0]


@app.before_request
def before_requre():
    pat = re.compile(r'^/static')
    if re.search(pat, request.path):
        return
    if request.path == "/login":
        return
    if request.path == '/register':
        return
    email = session.get('email')
    if email:
        return None
    return redirect('/login')


if __name__ == '__main__':
    app.run()
