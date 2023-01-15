#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/15 09:24
# @Author  : 冉勇
# @Site    : 
# @File    : logger.py
# @Software: PyCharm
# @desc    :
import os
import logging
import colorlog
from back.app import settings
from logging.handlers import RotatingFileHandler
from datetime import datetime



# 配置日志文件名称及路径
log_path = settings.LOG_PATH  # log_path为存放日志的路径
if not os.path.exists(log_path):
    os.mkdir(log_path)  # 若不存在logs文件夹，则自动创建

log_colors_config = {
    # 终端输出日志颜色配置
    'DEBUG': 'white',
    'INFO': 'cyan',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

default_formats = {
    # 终端输出格式
    'color_format': '%(log_color)s%(asctime)s-%(name)s-%(filename)s-[line:%(lineno)d]-%(levelname)s-[日志信息]: %(message)s',
    # 日志输出格式
    'log_format': '%(asctime)s - %(name)s - %(filename)s - [line:%(lineno)d] - %(levelname)s - [日志信息]: %(message)s'
}


class HandleLog():
    """
    先创建日志记录器（logging.getLogger），然后再设置日志级别（logger.setLevel），
    接着再创建日志文件，也就是日志保存的地方（logging.FileHandler），然后再设置日志格式（logging.Formatter），
    最后再将日志处理程序记录到记录器（addHandler）
    """

    def __init__(self, log_name):
        self.__now_time = datetime.now().strftime('%Y-%m-%d')  # 当前日期格式化

        # 收集所有日志文件，名称为：[日志名称] 2020-01-01-all.log；收集错误日志信息文件，名称为：[日志名称] 2020-01-01-error.log
        # 其中，[日志名称]为调用日志时的传入参数
        self.__all_log_path = os.path.join(log_path, log_name + " " + self.__now_time + "-all" + ".log")  # 收集所有日志信息文件
        self.__error_log_path = os.path.join(log_path,
                                             log_name + " " + self.__now_time + "-error" + ".log")  # 收集错误日志信息文件

        # 配置日志记录器及其级别 设置默认日志记录器记录级别为DEBUG
        self.__logger = logging.getLogger()  # 创建日志记录器
        self.__logger.setLevel(logging.DEBUG)  # 设置默认日志记录器记录级别

    @staticmethod
    def __init_logger_handler(log_path):
        """
        创建日志记录器handler，用于收集日志
        :param log_path: 日志文件路径
        :return: 日志记录器
        """
        # 写入文件，如果文件超过1M大小时，切割日志文件
        logger_handler = RotatingFileHandler(filename=log_path, maxBytes=1 * 1024 * 1024,
                                             encoding='utf-8')  # 可以设置 backupCount=3 在切割日志文件后仅保留3个文件
        return logger_handler

    @staticmethod
    def __init_console_handle():
        """创建终端日志记录器handler，用于输出到控制台"""
        return colorlog.StreamHandler()

    def __set_log_handler(self, logger_handler, level=logging.DEBUG):
        """
        设置handler级别并添加到logger收集器
        :param logger_handler: 日志记录器
        :param level: 日志记录器级别
        """
        logger_handler.setLevel(level=level)
        self.__logger.addHandler(logger_handler)  # 添加到logger收集器

    def __set_color_handle(self, console_handle):
        """
        设置handler级别并添加到终端logger收集器
        :param console_handle: 终端日志记录器
        :param level: 日志记录器级别
        """
        console_handle.setLevel(logging.DEBUG)
        self.__logger.addHandler(console_handle)

    @staticmethod
    def __set_color_formatter(console_handle, color_config):
        """
        设置输出格式-控制台
        :param console_handle: 终端日志记录器
        :param color_config: 控制台打印颜色配置信息
        :return:
        """
        formatter = colorlog.ColoredFormatter(default_formats["color_format"], log_colors=color_config)
        console_handle.setFormatter(formatter)

    @staticmethod
    def __set_log_formatter(file_handler):
        """
        设置日志输出格式-日志文件
        :param file_handler: 日志记录器
        """
        formatter = logging.Formatter(default_formats["log_format"],
                                      datefmt='')  # datefmt用于设置asctime的格式，例如：%a, %d %b %Y %H:%M:%S 或者 %Y-%m-%d %H:%M:%S
        file_handler.setFormatter(formatter)

    @staticmethod
    def __close_handler(file_handler):
        """
        关闭handler
        :param file_handler: 日志记录器
        """
        file_handler.close()

    def __console(self, level, message):
        """构造日志收集器"""
        # 创建日志文件
        all_logger_handler = self.__init_logger_handler(self.__all_log_path)  # 收集所有日志文件
        error_logger_handler = self.__init_logger_handler(self.__error_log_path)  # 收集错误日志信息文件
        console_handle = self.__init_console_handle()

        # 设置日志文件格式
        self.__set_log_formatter(all_logger_handler)
        self.__set_log_formatter(error_logger_handler)
        self.__set_color_formatter(console_handle, log_colors_config)

        self.__set_log_handler(all_logger_handler)  # 设置handler级别并添加到logger收集器
        self.__set_log_handler(error_logger_handler, level=logging.ERROR)
        self.__set_color_handle(console_handle)

        if level == 'info':
            self.__logger.info(message)
        elif level == 'debug':
            self.__logger.debug(message)
        elif level == 'warning':
            self.__logger.warning(message)
        elif level == 'error':
            self.__logger.error(message, exc_info=True,
                                stack_info=True)  # exc_info=True, stack_info=True 用于在日志中记录堆栈信息，方便查看日志进行调试
        elif level == 'critical':
            self.__logger.critical(message, exc_info=True,
                                   stack_info=True)  # exc_info=True, stack_info=True 用于在日志中记录堆栈信息，方便查看日志进行调试

        self.__logger.removeHandler(all_logger_handler)  # 避免日志输出重复问题
        self.__logger.removeHandler(error_logger_handler)
        self.__logger.removeHandler(console_handle)

        self.__close_handler(all_logger_handler)  # 关闭handler
        self.__close_handler(error_logger_handler)

    def debug(self, message):
        self.__console('debug', message)

    def info(self, message):
        self.__console('info', message)

    def warning(self, message):
        self.__console('warning', message)

    def error(self, message):
        self.__console('error', message)

    def critical(self, message):
        self.__console('critical', message)
