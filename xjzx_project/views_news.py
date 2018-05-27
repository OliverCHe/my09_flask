from flask import Blueprint
from flask import render_template


#如果希望用户直接访问，则不添加前缀
news_blueprint=Blueprint('news',__name__)


@news_blueprint.route('/')
def index():
    return  render_template('news/index.html')