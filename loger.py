import logging
import time
from logging.handlers import RotatingFileHandler
import os, sys

class loger:
    def __init__(self):
        self.log_format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s: %(message)s'
        if not os.path.exists("./log/"):
            os.mkdir("./log/")
        self.log_filename = "./log/error_log.txt"
        self.write_log_file()
    
    def write_log_Onefilename(self):
        #只写在一个文件
        filename = self.log_filename.format(time.strftime("%Y-%m-%d",time.localtime(time.time())))
        logging.basicConfig(filename=filename, format=self.log_format, datefmt='%Y-%m-%d %H:%M:%S:%S %p', filemode='a+', level=logging.INFO)
    
    def write_log_file(self):
        #修改默认打印级别
        logging.getLogger().setLevel(logging.DEBUG)

        #打印到控制台
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)#设置控制台日志输出的级别。如果设置为logging.INFO，就不会输出DEBUG日志信息
        console.setFormatter(logging.Formatter(self.log_format))
        logging.getLogger().addHandler(console)
        
        #自动换文件
        handler = logging.handlers.RotatingFileHandler(filename=self.log_filename, maxBytes=10*1024*1024, backupCount=100)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(self.log_format))
        logging.getLogger().addHandler(handler)

if __name__ == '__main__':
    print('this is main !')
    loging = loger()
    while True:
        logging.debug('this is a debug level message')
        logging.info("this is a info level message")
        logging.warning("this is a warning level message")
        logging.error("this is a error level message")
        logging.critical("this is a critical level message")