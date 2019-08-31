from gunicorn.http.body import Body

from utils import log

from routes.routes_basic import (
    error,
)
from routes.routes_public import route_dict

# 用 from import as 来避免重名
from routes.routes_weibo import route_dict as routes_weibo


# 定义一个 class 用于保存请求的数据
class Request(object):
    # {'wsgi.errors': <gunicorn.http.wsgi.WSGIErrorsWrapper object at 0x7fa090b316d8>,
    # 'wsgi.version': (1, 0), 'wsgi.multithread': False, 'wsgi.multiprocess': True,
    # 'wsgi.run_once': False, 'wsgi.file_wrapper': <class 'gunicorn.http.wsgi.FileWrapper'>,
    # 'SERVER_SOFTWARE': 'gunicorn/19.7.1',
    # 'wsgi.input': <gunicorn.http.body.Body object at 0x7fa090b31e10>,
    # 'gunicorn.socket': <socket.socket fd=12, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0,
    # laddr=('127.0.0.1', 8000), raddr=('127.0.0.1', 51312)>,
    # 'REQUEST_METHOD': 'GET', 'QUERY_STRING': '', 'RAW_URI': '/', 'SERVER_PROTOCOL': HTTP/1.1','
    # 'HTTP_HOST': '127.0.0.1:8000', 'HTTP_USER_AGENT': 'curl/7.58.0', 'HTTP_ACCEPT': '*/*',
    # 'HTTP_COOKIE': 'session=vvvv', 'wsgi.url_scheme': 'http', 'REMOTE_ADDR': '127.0.0.1',
    # 'REMOTE_PORT': '51312', 'SERVER_NAME': '127.0.0.1', 'SERVER_PORT': '8000', 'PATH_INFO': '/', 'SCRIPT_NAME': ''}
    def __init__(self, environ):
        self.raw = environ
        self.path = environ['PATH_INFO']
        body: Body = environ['wsgi.input']
        # Body 流只能 read 一次, log 就没有了
        # log('body', body.read())
        self.body = body.read().decode(encoding='utf-8')
        log('self.body <{}>'.format(self.body))
        self.headers = environ
        # log('请求 headers', self.headers)
        self.cookies = {}
        self.query = {}
        self.add_fields()
        log('请求 path 和 query', self.path, self.query)
        log('请求 cookies', self.cookies)

    def add_fields(self):
        self.add_field(self.cookies, self.raw.get('HTTP_COOKIE', ''))
        self.add_field(self.query, self.raw.get('QUERY_STRING', ''))

    @classmethod
    def add_field(cls, field, raw):
        if raw != '':
            parts = raw.split('; ')
            for part in parts:
                k, v = part.split('=', 1)
                field[k] = v

    def form(self):
        log('self.body', self.body)
        if self.body != '':
            args = self.body.split('&')
            f = {}
            log('args', args)
            for arg in args:
                k, v = arg.split('=')
                f[k] = v
            log('form() 字典', f)
            return f
        else:
            return {}


def response_for_path(request):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    # 注册外部的路由
    r = route_dict()
    r.update(routes_weibo())
    response = r.get(request.path, error)
    return response(request)


class Response:
    def __init__(self, raw_data: bytes):
        # 只能 split 一次，因为 body 中可能有换行
        data = raw_data.decode(encoding='utf-8')
        raw_header, self.body = raw_data.split(b'\r\n\r\n', 1)
        header = raw_header.decode()
        h = header.split('\r\n')

        parts = h[0].split()
        self.status = '{} {}'.format(parts[1], parts[2])
        # log('响应状态', self.status)

        self.headers = {}
        self.add_headers(h[1:])
        # log('响应 headers', self.headers)

    def add_headers(self, header):
        """
        Cookie: user=test
        """
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v


def app(environ, start_response):
    # log('environ', environ)

    request = Request(environ)
    raw_response = response_for_path(request)
    response = Response(raw_response)

    log('response.status <{}>'.format(response.status))
    log('response.headers <{}>'.format(response.headers))
    log('len response.body <{}>'.format(len(response.body)))
    data = response.body
    headers = list(response.headers.items())
    status = response.status
    start_response(status, headers)
    # data = b"Hello, World!\n"
    # start_response("200 OK", [
    #     ("Content-Type", "text/plain"),
    #     ("Content-Length", str(len(data)))
    # ])
    return iter([data])
