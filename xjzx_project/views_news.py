from flask import Blueprint, jsonify, request
from flask import render_template


#如果希望用户直接访问，则不添加前缀
from flask import session

from models import NewsCategory, UserInfo, NewsInfo

news_blueprint=Blueprint('news',__name__)


@news_blueprint.route('/')
def index():
    category_list = NewsCategory.query.all()

    count_list = NewsInfo.query.order_by(NewsInfo.click_count.desc())[0:6]

    if "user_id" in session:
        user = UserInfo.query.get(session.get("user_id"))

    else:
        user = None

    return  render_template('news/index.html', category_list=category_list, title="首页", user=user, count_list=count_list)


@news_blueprint.route('/newslist')
def newslist():
    page = int(request.args.get("page", "1"))

    category_id = int(request.args.get("category_id","0"))

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

