import urllib.parse

from models.session import Session
from models.user import User
from routes.routes_basic import (
    template,
    current_user,
    login_required,
    html_response,
    redirect
)
from utils import log


def route_index(request):
    """
    主页的处理函数, 返回主页的响应
    """
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
    body = template('index.html')
    u = current_user(request)
    body = body.replace('{{username}}', u.username)
    r = header + '\r\n' + body
    return r.encode()


def route_login(request):
    """
    登录页面的路由函数
    """
    log('login, headers', request.headers)
    log('login, cookies', request.cookies)
    user_current = current_user(request)
    log('current user', user_current)

    form = request.form()
    user_login, result = User.login_user(form)
    result = urllib.parse.quote_plus(result)
    if user_login is not None:
        session_id = Session.add(user_login.id)
        headers = {'Set-Cookie': 'session_id={}'.format(session_id)}
    else:
        headers = {}

    # return redirect('/todo')
    return redirect('/login/view', result=result, headers=headers)


def route_login_view(request):
    """
    登录页面视图
    """

    log('login, headers', request.headers)
    log('login, cookies', request.cookies)
    user = current_user(request)
    log('current user', user)

    result = request.query.get('result', '')
    result = urllib.parse.unquote_plus(result)

    return html_response(
        'login.html', result=result, username=user.username
    )


def route_register_view(request):
    user = current_user(request)
    result = request.query.get('result', '')
    result = urllib.parse.unquote_plus(result)
    return html_response(
        'register.html', result=result, username=user.username
    )


def route_register(request):
    form = request.form()
    result = User.register_user(form)
    # 换行符需要编码，不然显示不全
    result = urllib.parse.quote_plus(result)
    return redirect('/register/view', result=result)


def route_static(request):
    """
    静态资源的处理函数, 读取图片并生成响应返回
    """
    log('route_static')
    filename: str = request.query['file']
    path = 'static/{}'.format(filename)

    if filename.endswith('.gif'):
        content_type = b'Content-Type: image/gif'
    elif filename.endswith('.js'):
        content_type = b'Content-Type: application/javascript'
    elif filename.endswith('.css'):
        content_type = b'Content-Type: text/css'
    else:
        raise ValueError('不支持的后缀名', filename)

    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\n' + content_type
        r = header + b'\r\n\r\n' + f.read()
        return r


def route_dict():
    """
    路由字典
    key 是路由(路由就是 path)
    value 是路由处理函数(就是响应)
    """
    # f = login_required(route_message)
    # route_index(request)
    # f(request)
    d = {
        '/': route_index,
        '/static': route_static,
        '/login': route_login,
        '/login/view': route_login_view,
        '/register/view': route_register_view,
        '/register': route_register,
    }
    return d
