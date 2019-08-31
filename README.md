# HandMade_Server-And-MVC_WebFrame
由原始 Socket 连接建造 Web 服务器 + 自制 MVC web 框架
===


简介
---
自制 HTTP/WSGI SERVER + MVC web 框架:
    i. SERVER:
        1) 起点是一个 Socket 链接
        2) 面向的请求协议经过了一次升级:
            a) HTTP 协议
            b) WSGI 协议 
                i) 利用面向对象的方式, 把请求和响应这两个原生的字符串提取为两个类, Request 和 Response, 抽象出来之后操作更方便
        3) 多线程处理请求
        4) 交给路由函数
    ii. MVC 框架:
        1) M:
            a) 自制 基于 MySQL  语句的 ORM, modelPro
        2) V:
            a) 利用 Jinja2 渲染
        3) C: 
            a) 用字典完成路由注册, 利用了 Python 的高阶函数
            
# 功能演示:
---
- 针对 WSGI 协议进行上层 API 封装, 对 WSGI 请求响应的数据格式做清洗 可成功解析 WSGI 请求并成功响应.
- 支持 WSGI 协议之后, 可用 Gunicorn 应用服务器托管自制的 Web MVC 框架
    - ![](img-show/myserver-Gunicorn.gif)
