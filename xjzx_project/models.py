from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

pymysql.install_as_MySQLdb()

db = SQLAlchemy()


class BaseModel(object):
    createTime = db.Column(db.DateTime, default=datetime.now())
    modTime = db.Column(db.DateTime, default=datetime.now())
    isDelete = db.Column(db.Boolean, default=True)


tb_news_collect = db.Table('tb_user_news',
                           db.Column('user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
                           db.Column('news_id', db.Integer, db.ForeignKey('news_info.id'),primary_key=True))

tb_user_follow = db.Table('tb_user_follow',
                          db.Column('follow_user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True),
                          db.Column('follow_by_user_id', db.Integer, db.ForeignKey('user_info.id'), primary_key=True))


class NewsCategory(db.Model, BaseModel):
    __tablename__ = 'news_category'
    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(16))

    news = db.relationship('NewsInfo', backref='category', lazy='danamic')


class NewsComment(db.Model, BaseModel):
    __tablename__ = 'user_comment'
    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news_info.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    comment_content = db.Column(db.String(256))
    nice_count = db.Column(db.Integer, default=0)
    comment_id = db.Column(db.Integer, db.ForeignKey('user_comment.id'))


    user = db.relationship('UserInfo', backref='user', lazy='danamic')

    comments = db.relationship('NewsComment', lazy='danamic')


class NewsInfo(db.Model, BaseModel):
    __tablename__ = 'news_info'
    id = db.Column(db.Integer, primary_key=True)
    news_title = db.Column(db.String(32))
    news_type = db.Column(db.Integer, db.ForeignKey('news_category.id'))
    news_summary = db.Column(db.String(256))
    news_content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user_info.id'))
    click_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    varify_status = db.Column(db.SmallInteger, default=1)
    refuse_reason = db.Column(db.String(128), default='')

    comments = db.relationship('NewsComment', backref='news', lazy='danamic', order_by='NewsComment.id.desc()')


class UserInfo(db.Model,BaseModel):
    __tablename__ = 'user_info'
    id = db.Column(db.Integer, primary_key=True)
    portrait = db.Column(db.String(50), default='user_pic.png')
    nick_name = db.Column(db.String(20))
    signature = db.Column(db.String(200))
    public_count = db.Column(db.Integer, default=0)
    fans_count = db.Column(db.Integer, default=0)
    mobile = db.Column(db.String(11))
    password_hash = db.Column(db.String(200))
    gender = db.Column(db.Boolean, default=False)
    isAdmin = db.Column(db.Boolean, default=False)

    news = db.relationship('NewsInfo', backref='user', lazy='danamic')

    comments = db.relationship('NewsComment', backref='user', lazy='danamic')

    # 用户收藏了什么新闻
    news_collect = db.relationship(
        'NewsInfo',
        secondary = tb_news_collect,
        lazy='danamic'
    )

    # 用户关注的人
    follow_user_id = db.relationship(
        'UserInfo',
        secondary=tb_user_follow,
        primaryjoin= (db == tb_user_follow.c.follow_user_id),
        secondaryjoin= (db == tb_user_follow.c.follow_by_user_id),
        backref=db.backref('follow_by_user_id', lazy='danamic')
    )


    @property
    def password(self):
        pass


    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)


    def check_pwd(self, pwd):
        return check_password_hash(self.password_hash, pwd)