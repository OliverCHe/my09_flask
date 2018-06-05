from datetime import datetime

from flask import Blueprint, request, render_template, redirect, session, g, current_app

from models import UserInfo, NewsInfo

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')


@admin_blueprint.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('admin/login.html')


    elif request.method == "POST":
        # 接受
        admin_account = request.form.get("username")
        admin_pwd = request.form.get("password")

        # 验证
        if not all([admin_account, admin_pwd]):
            print("222222222")
            return render_template('admin/login.html', error_tip="请填写管理员账号密码", username=admin_account,
                                   password=admin_pwd)

        admin = UserInfo.query.filter(UserInfo.mobile == admin_account, UserInfo.isAdmin == True).first()
        # admin = UserInfo.query.filter_by(isAdmin=True, mobile=admin_account).first()

        print(admin)
        if admin is not None:
            if admin.check_pwd(admin_pwd):
                session["admin_id"] = admin.id
                return redirect("/admin/")
            else:
                return render_template('admin/login.html', error_tip="密码错误", username=admin_account, password=admin_pwd)
        else:
            return render_template('admin/login.html', error_tip="管理员账户不存在或没有权限", username=admin_account,
                                   password=admin_pwd)


@admin_blueprint.route('/logout')
def logout():
    del session["admin_id"]
    return redirect("/admin/login")


# 请求勾子, 每次请求都验证管理员登陆状态
@admin_blueprint.before_request
def before_request():
    print(request.path)
    if request.path != "/admin/login":
        if "admin_id" not in session:
            return redirect("/admin/login")
        g.admin = UserInfo.query.get(session.get("admin_id"))


@admin_blueprint.route('/')
def index():
    return render_template('admin/index.html')


@admin_blueprint.route('/user_count')
def user_count():
    # 用户总数量
    total_user = UserInfo.query.filter_by(isAdmin=False).count()

    now = datetime.now()

    # 月用户量
    month_first_day = datetime(now.year, now.month, 1)
    month_user = UserInfo.query.filter(UserInfo.isAdmin == False, UserInfo.createTime >= month_first_day).count()

    # 日用户量
    today_first = datetime(now.year, now.month, now.day)
    day_user = UserInfo.query.filter(UserInfo.isAdmin == False, UserInfo.createTime >= today_first).count()

    # 用redis存储用户登陆情况
    key = "login%d_%d_%d" % (now.year, now.month, now.day)
    hour_list = current_app.redis_client.hkeys(key)

    print(hour_list)
    hour_list = [hour.decode() for hour in hour_list]

    hour_user_list = []
    for hour in hour_list:
        hour_user = int(current_app.redis_client.hget(key, hour))
        hour_user_list.append(hour_user)

    return render_template('admin/user_count.html',
                           total_user=total_user,
                           month_user=month_user,
                           day_user=day_user,
                           hour_list=hour_list,
                           hour_user_list=hour_user_list
                           )


@admin_blueprint.route('/user_list/')
def user_list():
    page = int(request.args.get("page", "1"))

    pagination = UserInfo.query.filter_by(isAdmin=False).order_by(UserInfo.id.desc()).paginate(page, 9, False)

    all_user_list = pagination.items

    total_page = pagination.pages

    return render_template('admin/user_list.html', all_user_list=all_user_list, total_page=total_page, page=page)


@admin_blueprint.route('/news_review')
def news_review():
    page = int(request.args.get("page", "1"))

    pagination = NewsInfo.query.order_by(NewsInfo.modTime.desc()).paginate(page, 10, False)

    all_news_list = pagination.items

    total_page = pagination.pages

    return render_template('admin/news_review.html', all_news_list=all_news_list, total_page=total_page, page=page)


@admin_blueprint.route('/news_review/<int:news_id>', methods=["GET", "POST"])
def news_review_detail(news_id):
    if request.method == "GET":
        news = NewsInfo.query.get(news_id)

        return render_template('admin/news_review_detail.html', news=news)


@admin_blueprint.route('/news_edit')
def news_edit():
    return render_template('admin/news_edit.html')


@admin_blueprint.route('/news_edit_detail')
def news_edit_detail():
    return render_template('admin/news_edit_detail.html')


@admin_blueprint.route('/news_type')
def news_type():
    return render_template('admin/news_type.html')
