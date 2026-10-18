"""
通用辅助函数
"""
import hashlib


def fmt_time(value):
    """
    格式化时间为字符串
    :param value: datetime 对象
    :return: 'YYYY-MM-DD HH:MM:SS' 字符串，空值返回 None
    """
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else None


def md5(text):
    """
    计算字符串的 MD5 值
    :param text: 原始字符串
    :return: 32 位小写 MD5 字符串
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()
