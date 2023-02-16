import paramiko
from flask import Flask, render_template, request, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy
from database import Host
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@10.0.0.10:3306/demo'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'l%3ya7fn3moipdpcltj(tdfcv5^@lj=t5d&72levvls+y*@_4^'
db = SQLAlchemy(app)


@app.route("/")
def index():
    # 从数据库读取
    data = db.session.query(Host)
    return render_template('index.html', data=data)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == "POST":
        ip = request.form['ip']
        port = request.form['port']
        username = request.form['username']
        password = request.form['password']
        host = Host(ip=ip, port=port, username=username, password=password)
        db.session.add(host)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == "GET":
        id_num = request.args.get("id")
        db.session.query(Host).filter_by(id=id_num).delete()
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/ssh', methods=['GET', 'POST'])
def ssh():
    if request.method == "GET":
        id = request.args.get("id")
        users = db.session.query(Host).all()
        for user in users:
            if int(user.__dict__.get("id")) == int(id):
                ip = user.__dict__.get("ip")
                password = user.__dict__.get("password")
                port = int(user.__dict__.get("port"))
                username = user.__dict__.get("username")
                print(ip, password, port, username)
    ssh_cmd(ip=ip, port=port, username=username, password=password)
    return render_template('ssh.html')


def ssh_cmd(ip, port, username, password):
    tran = paramiko.Transport((ip, port))
    tran.start_client()
    tran.auth_password(username, password)
    chan = tran.open_session()
    chan.get_pty(height=1312, width=1312)
    chan.invoke_shell()
    sessions = chan

    # 出现消息后,率先执行此处
    @socketio.on("message", namespace="/Socket")
    def socket(message):
        # print("接收到消息:", message)
        sessions.send(message)
        ret = sessions.recv(4096)
        socketio.emit("response", {"Data": ret.decode("utf-8")}, namespace="/Socket")
        print(message)

    # 当websocket连接成功时,自动触发connect默认方法
    @socketio.on("connect", namespace="/Socket")
    def connect():
        ret = sessions.recv(4096)
        socketio.emit("response", {"Data": ret.decode("utf-8")}, namespace="/Socket")
        print("链接建立成功..")

    # 当websocket连接失败时,自动触发disconnect默认方法
    @socketio.on("disconnect", namespace="/Socket")
    def disconnect():
        print("链接建立失败..")


if __name__ == '__main__':
    app.run(port=80, debug=True)
