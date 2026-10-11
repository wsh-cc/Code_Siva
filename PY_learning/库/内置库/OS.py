#https://blog.csdn.net/yw1013/article/details/134093810?ops_request_misc=elastic_search_misc&request_id=f828cc53f3dd1307c1b61bfa3e31ea6d&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-134093810-null-null.142^v102^control&utm_term=pythonos%E5%BA%93%E7%9A%84%E4%BD%BF%E7%94%A8&spm=1018.2226.3001.4187
import os
 
# 分割路径名
dirname, basename = os.path.split('/home/user/file.txt')
print('Directory:', dirname)  # 输出：/home/user
print('File:', basename)  # 输出：file.txt
 
# 检查路径名是否存在
print(os.path.exists('/home/user'))  # 输出：True 或 False
 
# 检查路径名是否是一个文件
print(os.path.isfile('/home/user/file.txt'))  # 输出：True 或 False
 
# 检查路径名是否是一个目录
print(os.path.isdir('/home/user'))  # 输出：True 或 False

# import os
 
# 检查当前用户是否有权访问指定的文件
accessible = os.access("file.md", os.R_OK)#可以读取
 
# 输出结果
print("Accessible:", accessible)

# import os
 
# 更改指定文件的权限模式
os.chmod("file.md", os.R_OK)
 
# 输出结果
print("Permissions changed for file.md")

# import os
 
# 获取当前工作目录的字节对象
cwd = os.getcwdb()
 
# 输出当前工作目录
print("Current working directory:", cwd)
print("all:", os.listdir())
print('-'*20)
data=os.walk(r'D:\Python_code\高级特性')
for file_path,folder,files in data:#第一个是文件路径，第二个是文件夹，第三个是文件
        # print(file_path)
        # print(folder)
        # print(files)
        # print('-'*20)
    for file in files:
         if file.endswith('.py'):
        # if os.path.splitext(file)[1]=='.py':#获取文件的后缀名
            print(os.path.join(file_path ,file))
import sys
# sys.path.append(r'D:\Python_code\basic_study\函数测试')
