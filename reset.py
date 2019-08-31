import pymysql

from models.comment import Comment
from models.user import User
from models.session import Session
from models.weibo import Weibo
from utils import random_string


def pymysql_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='zaoshuizaoqi',
        # db='myserver',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def reset_all_tables():
    connection = pymysql_connection()
    with connection.cursor() as cursor:
        cursor.execute('DROP DATABASE IF EXISTS `myserver`')
        cursor.execute('CREATE DATABASE `myserver` CHARACTER SET utf8mb4')
        cursor.execute('USE `myserver`')

        cursor.execute(User.sql_create)
        cursor.execute(Session.sql_create)
        cursor.execute(Weibo.sql_create)
        cursor.execute(Comment.sql_create)
    connection.commit()
    connection.close()

    form = dict(
        username='nan',
        password='123',
    )
    User.register_user(form)
    u, result = User.login_user(form)
    assert u is not None, result

    session_id = random_string()
    form = dict(
        session_id=session_id,
        user_id=u.id,
    )
    Session.new(form)
    s: Session = Session.one(session_id=session_id)
    assert s.session_id == session_id

    form = dict(
        content='hello',
        user_id=u.id,
    )
    w = Weibo.new(form)
    assert w.content == 'hello'

    form = dict(
        content='hi',
        user_id=u.id,
        weibo_id=w.id,
    )
    c = Comment.new(form)
    assert c.content == 'hi'


# noinspection SqlNoDataSourceInspection,SqlResolve
def test():
    reset_all_tables()


if __name__ == '__main__':
    test()
