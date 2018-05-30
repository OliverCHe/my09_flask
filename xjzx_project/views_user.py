import random

import re
from flask import Blueprint, render_template, session, make_response, jsonify, redirect
from flask import current_app
from flask import request

from utile.captcha.captcha import captcha
from utile.ytx_sdk.ytx_send import sendTemplateSMS

from models import UserInfo, db

import functools
from utile.qiniu_xjzx import upload_pic


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


@user_blueprint.route('/mobile')
def mobile():
    if not UserInfo.query.filter_by(mobile=mobile).first():
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


# 验证user_id是否存在于session中
def login_verify(view_func):
    @functools.wraps(view_func)
    def inner_func(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/")
        return view_func(*args, **kwargs)
    return inner_func



@user_blueprint.route('/')
@login_verify
def index():
    user_id = session.get("user_id")

    user = UserInfo.query.get(user_id)

    return render_template("news/user.html", user=user, title="用户中心")


@user_blueprint.route('/user_base_info', methods=["GET", "POST"])
@login_verify
def user_base_info():
    user_id = session.get("user_id")
    user = UserInfo.query.get(user_id)
    if request.method == "GET":
        print("222222")
        return render_template("news/user_base_info.html", user=user)
    elif request.method == 'POST':
        req_dict = request.form
        signature = req_dict.get("signature")
        nick_name = req_dict.get("nick_name")
        gender = req_dict.get("gender")

        print("11111111")
        user.signature = signature
        user.nick_name = nick_name
        user.gender = True if gender == "True" else False

        try:
            db.session.commit()
        except:
            current_app.logger_xjzx.error("修改用户基本信息时连接数据库失败")
            return jsonify(result=2)

        return jsonify(result=1)



@user_blueprint.route('/user_pic_info', methods=["GET", "POST"])
@login_verify
def user_pic_info():
    user_id = session['user_id']
    user = UserInfo.query.get(user_id)

    if request.method == 'GET':
        return render_template('news/user_pic_info.html', user=user)
    elif request.method=='POST':
        f1 = request.files.get("portrait")
        f1_name = upload_pic(f1)
        print(f1_name)
        user.portrait = f1_name

        db.session.commit()


        return jsonify(result=1, portrait_url = user.portrait_url)


@user_blueprint.route('/user_follow')
@login_verify
def user_follow():
    return render_template("news/user_follow.html")


@user_blueprint.route('/user_pass_info')
@login_verify
def user_pass_info():
    return render_template("news/user_pass_info.html")


@user_blueprint.route('/user_collection')
@login_verify
def user_collection():
    return render_template("news/user_collection.html")


@user_blueprint.route('/user_news_release')
@login_verify
def user_news_release():
    return render_template("news/user_news_release.html")


@user_blueprint.route('/user_news_list')
@login_verify
def user_news_list():
    return render_template("news/user_news_list.html")



