"""

"""
from os import path
import inspect

def save_path_dir(file_name:str)->str:
    """
    获取当前文件所在目录的绝对路径，并将其与指定的文件名拼接起来，返回完整的文件路径。
    """
    current_file_path = inspect.stack()[1].filename
    # current_file_path = r"D:\Python_code\Web Crawler\Download"
    return path.join(path.dirname(current_file_path), file_name)

def save_path_inDownload(file_name:str)->str:
    """
    
    """
    current_file_path = r"D:\CODE\Web Crawler\Download"
    return path.join(current_file_path, file_name)