import random

import re
from flask import Blueprint, render_template, session, make_response, jsonify, redirect
from flask import current_app
from flask import request

from utile.captcha.captcha import captcha
from utile.ytx_sdk.ytx_send import sendTemplateSMS

from models import UserInfo, db, NewsInfo, NewsCategory

import functools
from utile.qiniu_xjzx import upload_pic

user_blueprint = Blueprint('user', __name__, url_prefix='/user')


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
            return jsonify(result=3, portrait_url=user.portrait_url, nick_name=user.nick_name)
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
    elif request.method == 'POST':
        f1 = request.files.get("portrait")
        f1_name = upload_pic(f1)
        print(f1_name)
        user.portrait = f1_name

        db.session.commit()

        return jsonify(result=1, portrait_url=user.portrait_url)


@user_blueprint.route('/user_follow')
@login_verify
def user_follow():
    user_id = session.get("user_id")
    user = UserInfo.query.get(user_id)

    current_page = int(request.args.get("current_page", "1"))

    follow_obj = user.follow_user.paginate(current_page, 4, False)

    follow_list = follow_obj.items
    total_page = follow_obj.pages

    return render_template("news/user_follow.html",
                           follow_list=follow_list,
                           total_page=total_page,
                           current_page=current_page
                           )


@user_blueprint.route('/user_pass_info', methods=["GET", "POST"])
@login_verify
def user_pass_info():
    if request.method == "GET":
        return render_template("news/user_pass_info.html")
    elif request.method == "POST":
        dict1 = request.form
        current_pwd = dict1.get("current_pwd")
        new_pwd = dict1.get("new_pwd")
        confirm_pwd = dict1.get("confirm_pwd")

        if not all([current_pwd, new_pwd, confirm_pwd]):
            return render_template("news/user_pass_info.html", error_tip="输入框不能有空")

        if not re.match(r'[a-zA-Z0-9_]{6,20}', current_pwd):
            return render_template("news/user_pass_info.html", error_tip="输入的旧密码有误")
        elif not re.match(r'[a-zA-Z0-9_]{6,20}', new_pwd):
            return render_template("news/user_pass_info.html", error_tip="输入的新密码格式有误")
        elif new_pwd != confirm_pwd:
            return render_template("news/user_pass_info.html", error_tip="两次输入的密码不一致")
        else:
            user_id = session.get("user_id")
            user = UserInfo.query.get(user_id)

            if not user.check_pwd(current_pwd):
                return render_template("news/user_pass_info.html", error_tip="输入的旧密码有误")

            user.password = new_pwd
            db.session.commit()
            return render_template("news/user_pass_info.html", error_tip="修改成功")


@user_blueprint.route('/user_collection')
@login_verify
def user_collection():
    user_id = session.get("user_id")
    user = UserInfo.query.get(user_id)

    current_page = int(request.args.get("current_page", "1"))
    # print(current_page)

    paginate_obj = user.news_collect.order_by(NewsInfo.id.desc()).paginate(current_page, 6, False)

    news_list = paginate_obj.items

    total_page = paginate_obj.pages

    return render_template("news/user_collection.html",
                           news_list=news_list,
                           total_page=total_page,
                           current_page=current_page
                           )


@user_blueprint.route('/user_news_release', methods=["GET", "POST"])
@login_verify
def user_news_release():
    category_list = NewsCategory.query.all()
    news_id = request.args.get("news_id")

    if request.method == "GET":
        if news_id is None:
            return render_template("news/user_news_release.html",
                                   category_list=category_list,
                                   news=None
                                   )
        else:
            news = NewsInfo.query.get(news_id)

            return render_template("news/user_news_release.html",
                                   category_list=category_list,
                                   news=news
                                   )

    elif request.method == "POST":
        dict1 = request.form

        title = dict1.get("news_title")
        category = dict1.get("news_category")
        summary = dict1.get("news_summary")
        content = dict1.get("content")
        pic = request.files.get("news_pic")

        if news_id is None:
            if not all([title, category, summary, pic, content]):
                return render_template("news/user_news_release.html",
                                       category_list=category_list,
                                       error_tip="请完整填写信息",
                                       news=None
                                       )
        else:
            news = NewsInfo.query.get("news_id")
            if not all([title, category, summary, content]):
                return render_template("news/user_news_release.html",
                                       category_list=category_list,
                                       error_tip="请完整填写信息",
                                       news=news
                                       )

        if news_id is None:
            news = NewsInfo()
        else:
            news = NewsInfo.query.get("news_id")

        news.news_title = title
        news.news_summary = summary
        news.news_type = category
        news.news_content = content
        news.user_id = session.get("user_id")

        if pic:
            filename = upload_pic(pic)
            news.news_pic = filename

        try:
            db.session.add(news)
            db.session.commit()
        except:
            current_app.logger_xjzx.error("用户发布修改新闻写入数据库错误")
            return render_template("news/user_news_release.html",
                                   category_list=category_list,
                                   error_tip="服务器发生异常"
                                   )

        return redirect("/user/user_news_list")


@user_blueprint.route('/user_news_list')
@login_verify
def user_news_list():
    user_id = session.get("user_id")
    user = UserInfo.query.get(user_id)
    print(user_id)

    current_page = request.args.get("current_page")

    news_obj = user.news.order_by(NewsInfo.modTime.desc()).paginate(current_page, 6, False)
    print(news_obj)
    news_list = news_obj.items
    print(news_list)
    total_page = news_obj.pages

    return render_template("news/user_news_list.html",
                           current_page=current_page,
                           news_list=news_list,
                           total_page=total_page
                           )
