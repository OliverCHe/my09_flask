import random

import re
from flask import Blueprint, render_template, session, make_response, jsonify
from flask import current_app
from flask import request

from utile.captcha.captcha import captcha
from utile.ytx_sdk.ytx_send import sendTemplateSMS

from models import UserInfo, db

user_blueprint=Blueprint('user',__name__,url_prefix='/user')


@user_blueprint.route('/imagecode')
def imagecode():
    name, text, buffer = captcha.generate_captcha()

    session['image_code'] = text

    response = make_response(buffer)
    response.mimetype = 'image/png'
    return response


@user_blueprint.route('/smscode')
def smscode():
    sms_dict = request.args
    mobile = sms_dict.get('mobile')
    image_code = sms_dict.get('image_code').upper()

    if image_code != session.get('image_code'):
        return jsonify(result=2)

    sms_code = random.randint(1000, 9999)
    session['sms_code'] = sms_code

    try:
        # sendTemplateSMS(mobile, [sms_code, "5"], 1)
        print(sms_code)
    except:
        current_app.logger_xjzx.error("用户注册时发送短信失败")
        return jsonify(result=3)
    else:
        return jsonify(result=1)


@user_blueprint.route('/register', methods=['POST'])
def register():
    reg_dict = request.form
    mobile = reg_dict.get('mobile')
    image_code = reg_dict.get('image_code').upper()
    sms_code = reg_dict.get('sms_code')
    pwd = reg_dict.get('password')

    if not all([mobile, image_code, sms_code, pwd]):
        return jsonify(result=1)
    elif image_code != session.get('image_code'):
        return jsonify(result=2)
    elif int(sms_code) != session.get('sms_code'):
        return jsonify(result=3)
    elif not re.match(r'[a-zA-Z0-9_]{6,20}', pwd):
        return jsonify(result=4)

    elif UserInfo.query.filter_by(mobile=mobile).count():
        return jsonify(result=5)

    user = UserInfo()
    user.mobile = mobile
    user.password = pwd
    user.nick_name = mobile

    try:
        db.session.add(user)
        db.session.commit()
    except:
        current_app.logger_xjzx.error('注册用户时数据库访问失败')
        return jsonify(result=6)
    else:
        return jsonify(result=7)


@user_blueprint.route('/login', methods=['POST'])
def login():
    log_dict = request.form
    mobile = log_dict.get("mobile")
    pwd = log_dict.get("password")

    if not all([mobile, pwd]):
        return jsonify(result=1)

    user = UserInfo.query.filter_by(mobile=mobile).first()
    # print(user.mobile)
    # print(user.password_hash)
    # print(user.check_pwd(pwd))
    if user:
        if user.check_pwd(pwd):
            session["user_id"] = user.id
            return jsonify(result=3, portrait=user.portrait, nick_name=user.nick_name)
        else:
            return jsonify(result=4)
    else:
        return jsonify(result=2)



@user_blueprint.route('/logout', methods=["POST"])
def logout():
    session.pop("user_id")
    return jsonify(result=1)




