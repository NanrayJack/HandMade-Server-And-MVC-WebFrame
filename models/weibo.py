from models.model_basic import SQLModel
from models.comment import Comment


# noinspection SqlDialectInspection
class Weibo(SQLModel):
    """
    评论类
    """
    # noinspection SqlNoDataSourceInspection
    sql_create = """
    CREATE TABLE `Weibo` (
        `id`         INT NOT NULL AUTO_INCREMENT,
        `content`    VARCHAR(255) NULL,
        `user_id`    INT NOT NULL,
        PRIMARY KEY (`id`)
    );
    """

    def __init__(self, form):
        super().__init__(form)
        self.content = form.get('content', '')
        # 和别的数据关联的方式, 用 user_id 表明拥有它的 user 实例
        self.user_id = form.get('user_id', None)

    def comments(self):
        cs = Comment.all(weibo_id=self.id)
        return cs
