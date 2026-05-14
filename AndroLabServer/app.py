import getopt
import sys
from cheroot import wsgi
from flask import Flask, request
from models import User, Account
from database import db_session

import simplejson as json
makejson = json.dumps

app = Flask(__name__)
DEFAULT_PORT_NO = 8888


def usageguide():
    print("InsecureBankv2 Backend-Server")
    print("Options:")
    print("  --port p    serve on port p (default 8888)")
    print("  --help      print this message")


@app.errorhandler(500)
def internal_servererror(error):
    print("[!]", error)
    return "Internal Server Error", 500


# ✅ LOGIN
@app.route('/login', methods=['POST'])
def login():
    user = request.form.get("username")
    password = request.form.get("password")

    u = User.query.filter_by(username=user).first()

    if not u:
        msg = "User Does not Exist"
    elif u.password != password:
        msg = "Wrong Password"
    else:
        msg = "Correct Credentials"

    return makejson({"message": msg, "user": user})


# ✅ GET ACCOUNTS
@app.route('/getaccounts', methods=['POST'])
def getaccounts():
    user = request.form.get("username")
    password = request.form.get("password")

    u = User.query.filter_by(username=user).first()

    from_acc = 0
    to_acc = 0

    if not u or u.password != password:
        msg = "Wrong Credentials so trx fail"
    else:
        msg = "Success"
        accounts = Account.query.filter_by(user=user).all()

        for acc in accounts:
            if acc.type == "from":
                from_acc = acc.account_number
            elif acc.type == "to":
                to_acc = acc.account_number

    return makejson({"message": msg, "from": from_acc, "to": to_acc})


# ✅ CHANGE PASSWORD
@app.route('/changepassword', methods=['POST'])
def changepassword():
    user = request.form.get("username")
    newpassword = request.form.get("newpassword")

    u = User.query.filter_by(username=user).first()

    if not u:
        msg = "Error"
    else:
        u.password = newpassword
        db_session.commit()
        msg = "Change Password Successful"

    return makejson({"message": msg})


# ✅ TRANSFER
@app.route('/dotransfer', methods=['POST'])
def dotransfer():
    user = request.form.get("username")
    password = request.form.get("password")

    from_acc = request.form.get("from_acc")
    to_acc = request.form.get("to_acc")
    amount = request.form.get("amount")

    u = User.query.filter_by(username=user).first()

    if not u or u.password != password:
        msg = "Wrong Credentials so trx fail"
    else:
        from_account = Account.query.filter_by(account_number=from_acc).first()
        to_account = Account.query.filter_by(account_number=to_acc).first()

        if from_account and to_account:
            from_account.balance -= int(amount)
            to_account.balance += int(amount)
            db_session.commit()
            msg = "Success"
        else:
            msg = "Invalid account"

    return makejson({
        "message": msg,
        "from": from_acc,
        "to": to_acc,
        "amount": amount
    })


# ✅ DEV LOGIN
@app.route('/devlogin', methods=['POST'])
def devlogin():
    user = request.form.get("username")
    return makejson({"message": "Correct Credentials", "user": user})


# ✅ MAIN
if __name__ == "__main__":
    port = DEFAULT_PORT_NO

    options, args = getopt.getopt(sys.argv[1:], "", ["help", "port="])
    for op, arg in options:
        if op == "--help":
            usageguide()
            sys.exit()
        elif op == "--port":
            port = int(arg)

    server = wsgi.Server(("0.0.0.0", port), app)
    print(f"Server running on port {port}")

    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()
