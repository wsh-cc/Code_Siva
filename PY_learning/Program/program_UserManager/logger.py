import logging

logging.basicConfig(#配置日志记录器
    #需要修改的文件路径
    filename="app.log",#日志文件名，日志将被写入这个文件
    level=logging.INFO,#日志级别，只有级别高于或等于这个级别的日志才会被记录，info debug warning error critical
    format="%(asctime)s - %(levelname)s - %(message)s"#日志格式，包含时间、日志级别和消息内容
)

logger = logging.getLogger()#创建一个logger对象，可以在其他模块中导入使用