# coding: utf-8
import os
import logging
import time
import sys

class logger(object):
    """
    处理日志类
    """

    def __init__(self):
        # 配置输出格式
        self.LOG_FORMAT = "%(asctime)s %(name)s %(funcName)s %(levelname)s %(pathname)s \n%(message)s"
        # 配置输出时间的格式
        self.DATE_FORMAT = '%Y-%m-%d  %H:%M:%S %a '
        # 配置日志输出位置
        self.path = os.path.dirname(__file__) + r"/logfile/" + time. \
            strftime("%Y-%m-%d", time.gmtime()) + ".log"
        self.setting()

    def setting(self):
        file_handler = logging.FileHandler(self.path, mode='a', encoding="utf8")
        file_handler.setFormatter(logging.Formatter(
            self.LOG_FORMAT, datefmt=self.DATE_FORMAT
        ))
        file_handler.setLevel(logging.INFO)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            self.LOG_FORMAT, datefmt=self.DATE_FORMAT
        ))
        console_handler.setLevel(logging.INFO)
        logging.basicConfig(
            level=min(logging.INFO, logging.DEBUG),
            format=self.LOG_FORMAT,
            datefmt=self.DATE_FORMAT,
            handlers=[file_handler, console_handler]
        )

    @staticmethod
    def debug(msg):
        logging.debug(msg)

    @staticmethod
    def info(msg):
        logging.info(msg)

    @staticmethod
    def warning(msg):
        logging.warning(msg)

    @staticmethod
    def error(msg):
        logging.error(msg)

    @staticmethod
    def critical(msg):
        logging.critical(msg)


if __name__ == '__main__':
    logger = logger()
