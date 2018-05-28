from flask import Blueprint
from flask import render_template


#如果希望用户直接访问，则不添加前缀
from flask import session

news_blueprint=Blueprint('news',__name__)


@news_blueprint.route('/')
def index():
    # if session.get("user_id") != None:
    #     user_id = session.get("user_id")
    #
    return  render_template('news/index.html')