from datetime import datetime

from flask import Blueprint, request, render_template, redirect, session, g, current_app, jsonify

from models import UserInfo, NewsInfo, NewsCategory, db
from utile.qiniu_xjzx import upload_pic

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
    # print(request.path)
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

    # print(hour_list)
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
    # page = int(request.args.get("page", "1"))
    #
    # pagination = NewsInfo.query.order_by(NewsInfo.modTime.desc()).paginate(page, 10, False)
    #
    # all_news_list = pagination.items
    #
    # total_page = pagination.pages
    #
    # return render_template('admin/news_review.html', all_news_list=all_news_list, total_page=total_page, page=page)
    return render_template('admin/news_review.html')
    # 因为同页面有搜索功能, 所以用局部刷新会比较好
    # 重新定义一个视图函数, 并利用ajax发出请求


@admin_blueprint.route('/news_review_ajax')
def news_review_ajax():
    page = int(request.args.get("page", "1"))
    input_text = request.args.get("input_text")
    print(input_text)

    pagination = NewsInfo.query
    if input_text:
        pagination = pagination.filter(NewsInfo.news_title.contains(input_text))
    pagination = pagination.order_by(NewsInfo.modTime.desc()).paginate(page, 6, False)

    news_list = pagination.items
    total_page = pagination.pages

    print(news_list)

    news_list2 = []
    for news_raw in news_list:
        dict1 = {
            "id": news_raw.id,
            "title": news_raw.news_title,
            "modTime": news_raw.modTime.strftime('%Y-%m-%d %H:%M:%S'),
            "status": news_raw.varify_status
        }

        news_list2.append(dict1)

    return jsonify(news_list=news_list2, total_page=total_page)


@admin_blueprint.route('/news_review/<int:news_id>', methods=["GET", "POST"])
def news_review_detail(news_id):
    news = NewsInfo.query.get(news_id)

    if request.method == "GET":
        return render_template('admin/news_review_detail.html', news=news)
    elif request.method == "POST":
        action = request.form.get('action')
        reason = request.form.get('reason')

        if action == "accept":
            news.varify_status = 2
            db.session.commit()
        else:
            news.varify_status = 3
            news.refuse_reason = reason
            db.session.commit()

        return redirect("/admin/news_review")


@admin_blueprint.route('/news_edit')
def news_edit():
    return render_template('admin/news_edit.html')


@admin_blueprint.route('/news_edit_json')
def news_edit_json():
    page = int(request.args.get("page", "1"))
    input_text = request.args.get("input_text")

    pagination = NewsInfo.query

    if input_text:
        pagination = pagination.filter(NewsInfo.news_title.contains(input_text))
    pagination = pagination.order_by(NewsInfo.modTime.desc()).paginate(page, 5, False)

    news_list = pagination.items
    total_page = pagination.pages

    news_list2 = []
    for news in news_list:
        dict1 = {
            "id": news.id,
            "title": news.news_title,
            "modTime": news.modTime.strftime("%Y-%m-%d %H:%M:%S")
        }
        news_list2.append(dict1)

    return jsonify(news_list=news_list2, total_page=total_page)


@admin_blueprint.route('/news_edit/<int:news_id>', methods=["GET", "POST"])
def news_edit_detail(news_id):
    news = NewsInfo.query.get(news_id)
    if request.method == "GET":
        category_list = NewsCategory.query.all()
        return render_template('admin/news_edit_detail.html', news=news, category_list=category_list)

    elif request.method == "POST":
        dict1 = request.form
        title = dict1.get('title')
        category_id = dict1.get('category_id')
        summary = dict1.get('summary')
        content = dict1.get('content')
        # 接收图片文件
        pic = request.files.get('pic')
        news.news_title = title
        news.news_type = int(category_id)
        news.news_summary = summary
        news.news_content = content
        news.modTime = datetime.now()

        if pic:
            filename = upload_pic(pic)
            news.news_pic = filename

        db.session.commit()

        return redirect("/admin/news_edit")


@admin_blueprint.route('/news_type')
def news_type():
    return render_template('admin/news_type.html')


@admin_blueprint.route('/news_type_list')
def news_type_list():
    category_list = NewsCategory.query.all()
    category_list2 = []

    for category in category_list:
        dict1 = {
            "id": category.id,
            "type_name": category.type_name
        }
        category_list2.append(dict1)

    return jsonify(result=1, category_list=category_list2)


@admin_blueprint.route('/news_type_add', methods=["POST"])
def news_type_add():
    name = request.form.get('name')

    if NewsCategory.query.filter_by(type_name=name).count():
        return jsonify(result=2)

    category = NewsCategory()

    category.type_name = name

    db.session.add(category)
    db.session.commit()

    return jsonify(result=1)


@admin_blueprint.route('/news_type_edit', methods=['POST'])
def news_type_edit():
    cid = request.form.get('id')
    name = request.form.get('name')
    # 判断名称是否重复
    name_exists = NewsCategory.query.filter_by(type_name=name).count()
    if name_exists > 0:
        return jsonify(result=2)
    # 修改
    category = NewsCategory.query.get(cid)
    category.name = name
    # 保存到数据库
    db.session.commit()
    # 响应
    return jsonify(result=1)
