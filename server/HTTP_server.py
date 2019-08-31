import json
import socket
import urllib.parse
import threading
from utils import log

from routes.routes_basic import (
    error,
)
from routes.routes_public import route_dict

# as 来避免重名
from routes.routes_weibo import route_dict as routes_weibo


# 定义一个 class 用于保存请求的数据
class Request(object):
    def __init__(self, raw_data):
        # 只能 split 一次，因为 body 中可能有换行
        header, self.body = raw_data.split('\r\n\r\n', 1)
        h = header.split('\r\n')

        parts = h[0].split()
        self.method = parts[0]
        path = parts[1]
        self.path = ""
        self.query = {}
        self.parse_path(path)
        log('请求 path 和 query', self.path, self.query)

        self.headers = {}
        self.cookies = {}
        self.add_headers(h[1:])
        log('请求 headers', self.headers)
        log('请求 cookies', self.cookies)

    def add_headers(self, header):
        """
        Cookie: user=test
        """
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v

        if 'Cookie' in self.headers:
            cookies = self.headers['Cookie']
            # 浏览器发来的 cookie 只有一个值
            parts = cookies.split('; ')
            for part in parts:
                k, v = part.split('=', 1)
                self.cookies[k] = v

    def form(self):
        body = urllib.parse.unquote_plus(self.body)
        log('form', self.body)
        log('form', body)
        args = body.split('&')
        f = {}
        log('args', args)
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        log('form() 字典', f)
        return f

    def json(self):
        data = json.loads(self.body)
        return data

    def parse_path(self, path):
        """
        输入: /path?message=test_message&author=test
        返回
        (path, {
            'message': 'test_message',
            'author': 'test',
        })
        """
        index = path.find('?')
        if index == -1:
            self.path = path
            self.query = {}
        else:
            path, query_string = path.split('?', 1)
            args = query_string.split('&')
            query = {}
            for arg in args:
                k, v = arg.split('=')
                query[k] = v
            self.path = path
            self.query = query


def request_from_connection(connection):
    request = b''
    buffer_size = 1024
    while True:
        r = connection.recv(buffer_size)
        request += r
        # 取到的数据长度不够 buffer_size 的时候，说明数据已经取完了。
        if len(r) < buffer_size:
            return request


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


def process_connection(connection):
    with connection:
        r = request_from_connection(connection)
        r = r.decode()
        # chrome, 会发空请求
        if len(r) > 0:
            # log('http 原始请求:<\n{}\n>'.format(r))
            # 把原始请求数据传给 Request 对象
            request = Request(r)
            # 用 response_for_path 函数来得到 path 对应的响应内容
            response = response_for_path(request)
            index = response.find(b'Content-Type: text/html')
            if index == -1:
                start = response.find(b'\r\n\r\n')
                gif_length = len(response[start:])
                gif_header = response[:start]
                log('http 响应头部: <{}> 内容长度：<{}>'.format(gif_header, gif_length))
            else:
                log("http 响应:<\n{}\n>".format(response.decode()))
            # 把响应发送给客户端
            connection.sendall(response)
        else:
            log('chrome 发来空请求')
            connection.sendall(b'')


def run(host, port):
    """
    启动服务器
    """
    # 初始化 socket 套路
    # 使用 with 可以保证程序中断的时候正确关闭 socket 释放占用的端口
    log('开始运行于', 'http://{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 无限循环来处理请求
        # 监听 接受 读取请求数据 解码成字符串
        # noinspection PyArgumentList
        s.listen()
        while True:
            connection, address = s.accept()
            log('请求 ip 和 端口 <{}>\n'.format(address))
            t = threading.Thread(target=process_connection, args=(connection,))
            t.start()


if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='localhost',
        port=3000,
    )
    run(**config)
