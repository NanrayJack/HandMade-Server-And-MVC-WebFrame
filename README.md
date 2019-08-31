基于原始 Socket 连接, 从无到有打造 Web 服务器 + 自制 MVC web 框架
===


简介
---
- SERVER:
    - 起点是一个 Socket 链接
    - 面向的请求协议经过了一次升级:
        - HTTP 协议
        - WSGI 协议 
            - 利用面向对象的方式, 把请求和响应这两个原生的字符串提取为两个类, Request 和 Response, 抽象出来之后操作更方便
    - 多线程处理请求
    - 交给路由函数
- MVC 框架:
    - Model:
        - 基于 JSON 文件键值对 (表) 实现数据持久化, 类似 Nosql 类数据库. 被替换为 Mysql
        - 自制基于 MySQL 语句的 ORM
            - 提供底层 Model 基类, 实现最常用增删改查类方法
                - 方法根据 (参数 / 具体子类) 拼接 sql 语句
            - 具体 Model 如 User, Weibo 继承基类
    - View:
        - 利用 Jinja2 渲染
    3) C: 
        - 用字典映射 url-route, 用多表 update 实现类似 flask 蓝图管理, 利用了 Python 的高阶函数
            
功能演示
---
- 针对 WSGI 协议进行上层 API 封装, 对 WSGI 请求响应的数据格式做清洗 可成功解析 WSGI 请求并成功响应.
- 支持 WSGI 协议之后, 可用 Gunicorn 应用服务器托管自制的 Web MVC 框架
    - ![](img-show/myserver-Gunicorn.gif)
