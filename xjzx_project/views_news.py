from flask import Blueprint, jsonify, request, abort
from flask import render_template

# 如果希望用户直接访问，则不添加前缀
from flask import session

from models import NewsCategory, UserInfo, NewsInfo, db, NewsComment

news_blueprint = Blueprint('news', __name__)


@news_blueprint.route('/')
def index():
    category_list = NewsCategory.query.all()

    count_list = NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]

    if "user_id" in session:
        user = UserInfo.query.get(session.get("user_id"))

    else:
        user = None

    return render_template('news/index.html', category_list=category_list, title="首页", user=user, count_list=count_list)


@news_blueprint.route('/newslist')
def newslist():
    page = int(request.args.get("page", "1"))

    category_id = int(request.args.get("category_id", "0"))

    pagination = NewsInfo.query
    if category_id:
        pagination = pagination.filter_by(news_type=category_id)

    pagination = pagination.order_by(NewsInfo.modTime.desc()).paginate(page, 4, False)

    news_list = pagination.items

    news_list2 = []

    for news in news_list:
        news_dict = {
            "id": news.id,
            "pic_url": news.pic_url,
            "news_title": news.news_title,
            "news_summary": news.news_summary,
            "portrait_url": news.user.portrait_url,
            "user_id": news.user.id,
            "user_nick_name": news.user.nick_name,
            "modTime": news.modTime
        }
        news_list2.append(news_dict)

    return jsonify(news_list=news_list2, page=page)


@news_blueprint.route('/<int:news_id>')
def detail(news_id):
    news = NewsInfo.query.get(news_id)

    if news is None:
        abort(404)

    if 'user_id' in session:
        user_id = session.get('user_id')
        user = UserInfo.query.get(user_id)

    else:
        user = None

    count_list = NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]

    return render_template("news/detail.html",
                           user=user,
                           news=news,
                           title=news.news_title,
                           count_list=count_list
                           )


@news_blueprint.route('/collect/<int:news_id>', methods=["POST"])
def news_collect(news_id):
    action = int(request.form.get('action', "1"))
    print(action)

    news = NewsInfo.query.get(news_id)
    if news is None:
        return jsonify(result=1)
    if 'user_id' not in session:
        return jsonify(result=2)

    user = UserInfo.query.get(session.get("user_id"))

    # 收藏
    if action == 1:

        if news in user.news_collect:
            return jsonify(result=4)
        user.news_collect.append(news)

    # 取消收藏
    else:
        if news not in user.news_collect:
            return jsonify(result=4)
        user.news_collect.remove(news)

    db.session.commit()

    return jsonify(result=3)


@news_blueprint.route('/comment/add', methods=["POST"])
def comment_add():
    news_id = int(request.form.get('news_id'))
    comment_content = request.form.get('comment_content')

    if not all([news_id, comment_content]):
        return jsonify(result=1)

    news = NewsInfo.query.get(news_id)

    if news is None:
        return jsonify(result=2)

    if 'user_id' not in session:
        return jsonify(result=3)

    else:
        user = UserInfo.query.get(session.get("user_id"))

    comment = NewsComment()
    comment.news_id = news_id
    comment.user_id = user.id
    comment.comment_content = comment_content
    news.comment_count += 1

    db.session.add(comment)
    db.session.commit()

    return jsonify(result=4, comment_count=news.comment_count)



@news_blueprint.route('/comment/list/<int:news_id>')
def comment_list(news_id):
    news = NewsInfo.query.get(news_id)

    if news is None:
        return jsonify(result=1)

    comment_list = news.comments.order_by(NewsComment.modTime.desc(), NewsComment.nice_count.desc())

    comment_list2 = []

    for comment in comment_list:
        dict1 = {
            "id": comment.id,
            "content": comment.comment_content,
            "create_time": comment.createTime,
            "nice_count": comment.nice_count,
            "nick_name": comment.user.nick_name,
            "portrait_url": comment.user.portrait_url
        }

        comment_list2.append(dict1)

    return jsonify(result=2, comment_list=comment_list2)