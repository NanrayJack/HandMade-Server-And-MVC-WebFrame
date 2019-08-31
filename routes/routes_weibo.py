from models.comment import Comment
from models.weibo import Weibo
from routes.routes_basic import (
    redirect,
    current_user,
    html_response,
    login_required,
)
from utils import log


@login_required
def index(request):
    """
    weibo 首页的路由函数
    """
    u = current_user(request)
    weibos = Weibo.all(user_id=u.id)
    # 替换模板文件中的标记字符串
    return html_response('weibo_index.html', weibos=weibos, user=u)


@login_required
def add(request):
    """
    用于增加新 weibo 的路由函数
    """
    u = current_user(request)
    form = request.form()
    f = dict(
        content=form['content'],
        user_id=u.id,
    )
    Weibo.new(f)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


@login_required
def delete(request):
    weibo_id = int(request.query['weibo_id'])
    Weibo.delete(weibo_id)
    return redirect('/weibo/index')


@login_required
def edit(request):
    weibo_id = int(request.query['weibo_id'])
    w = Weibo.one(id=weibo_id)
    return html_response('weibo_edit.html', weibo=w)


@login_required
def update(request):
    """
    用于增加新 weibo 的路由函数
    """
    form = request.form()
    weibo_id = int(form['weibo_id'])
    kwargs = dict(
        content=form['content']
    )
    Weibo.update(weibo_id, **kwargs)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')


@login_required
def comment_add(request):
    u = current_user(request)
    form = request.form()
    weibo_id = int(form['weibo_id'])

    kwargs = dict(
        weibo_id=weibo_id,
        content=form['content'],
        user_id=u.id,
    )
    Comment.new(kwargs)

    return redirect('/weibo/index')


def weibo_owner_required(route_function):
    def f(request):
        log('weibo_owner_required')
        u = current_user(request)
        id_key = 'weibo_id'
        if id_key in request.query:
            weibo_id = request.query[id_key]
        else:
            weibo_id = request.form()[id_key]
        w = Weibo.one(id=int(weibo_id))

        if w.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')

    return f


def comment_owner_required(route_function):
    def f(request):
        u = current_user(request)
        if 'id' in request.query:
            comment_id = request.query['id']
        else:
            comment_id = request.form()['id']
        c = Comment.one(id=int(comment_id))

        if c.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')
    return f


def comment_owner_or_weibo_owner_required(route_function):
    def f(request):
        u = current_user(request)
        if 'id' in request.query:
            comment_id = request.query['id']
        else:
            comment_id = request.form()['id']
        c = Comment.one(id=int(comment_id))

        # 对应这个评论的微博
        w = Weibo.one(id=c.weibo_id)

        log('w.user_id', w.user_id)
        log('u.id', u.id)
        if c.user_id == u.id or w.user_id == u.id:
            return route_function(request)
        else:
            return redirect('/weibo/index')
    return f


@comment_owner_or_weibo_owner_required
def comment_delete(request):
    comment_id = int(request.query['id'])
    Comment.delete(comment_id)
    return redirect('/weibo/index')


@comment_owner_or_weibo_owner_required
def comment_edit(request):
    comment_id = int(request.query['id'])
    c = Comment.one(id=comment_id)
    return html_response('comment_edit.html', comment=c)


@comment_owner_or_weibo_owner_required
def comment_update(request):
    form = request.form()
    kwargs = dict(
        content=form['content'],
    )
    Comment.update(id=form['id'], **kwargs)
    # 浏览器发送数据过来被处理后, 重定向到首页
    # 浏览器在请求新首页的时候, 就能看到新增的数据了
    return redirect('/weibo/index')



def route_dict():
    d = {
        '/weibo/index': index,
        '/weibo/add': add,
        '/weibo/delete': weibo_owner_required(delete),
        '/weibo/edit': weibo_owner_required(edit),
        '/weibo/update': weibo_owner_required(update),
        '/comment/add': comment_add,
    }
    return d
