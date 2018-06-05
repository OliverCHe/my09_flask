import random
from datetime import datetime

from flask import current_app
from flask_script.commands import Command

from models import UserInfo, db


class CreateAdminCommand(Command):
    def run(self):
        access_pwd = input("请输入权限密码: ")

        if access_pwd != "admin":
            print("密码错误")
            return

        print("-" * 20 + "创建管理员账号" + "-" * 20)

        admin_account = input("请输入管理员账号: ")
        admin_pwd = input("请输入密码: ")
        confirm_pwd = input("再一次输入密码: ")

        admin = UserInfo.query.filter(UserInfo.isAdmin == True, UserInfo.mobile == admin_account)

        if admin.count():
            print("账户已存在")
            return

        if admin_pwd != confirm_pwd:
            print("两次输入的密码不一致")
            return

        user = UserInfo()
        user.mobile = admin_account
        user.password = admin_pwd
        user.isAdmin = True

        db.session.add(user)
        db.session.commit()

        print("管理员账户创建成功")


class RegisterUserCommand(Command):
    def run(self):
        list1 = []
        for i in range(1,3000):
            user = UserInfo()
            user.nick_name = "用户%d" % i
            user.mobile = '用户%02d' % i
            user.createTime = datetime(2018, random.randint(1, 6), random.randint(1, 28))
            user.modTime = datetime(2018, random.randint(1, 6), random.randint(1, 28))
            list1.append(user)

        db.session.add_all(list1)
        db.session.commit()


class HourLoginCommand(Command):
    def run(self):
        now = datetime.now()
        key = "login%d_%d_%d" % (now.year, now.month, now.day)
        for i in range(8,20):
            current_app.redis_client.hset(key, '%02d:15' % i, random.randint(5000, 20000))
