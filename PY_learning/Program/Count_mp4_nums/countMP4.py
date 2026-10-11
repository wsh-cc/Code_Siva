import os
# from pydoc import cli
from moviepy import VideoFileClip

def count_mp4_duration(file_path:str)->float:
    """
    输入mp4文件路径
    返回mp4文件的时间    
    """
    clip = VideoFileClip(file_path,audio=False)#加载视频文件，设置audio=False以节省资源
    duration = clip.duration
    clip.close()  # 关闭视频文件,释放资源，重要
    return duration

def cnttime(directory):
    data=os.walk(directory)#生成器，返回一个三元组（dirpath路径, dirnames文件夹列表, filenames文件列表）
    try:
        sum_sound=0
        # mp4_nums=0
        for file_path,folder,files in data:#为什么能遍历完？因为os.walk会递归地遍历目录树，返回每个目录的路径、子目录列表和文件列表。每次迭代都会返回当前目录的信息，直到遍历完整个目录树。
            # print(file_path)
            # print(folder)
            # print(files)
            # print('-'*20)
        
                for file in files:
                    
                    if file.endswith('.mp4'):
                        # mp4_nums+=1
                        full_path = os.path.join(file_path, file)
                        duration = count_mp4_duration(full_path)
                        print(f" - {full_path}:{duration} seconds")
                        sum_sound += duration
                    else:continue
    except Exception :
        print("——"*40)
    else :print("——"*40) 
    # print(f"该文件夹下的{mp4_nums}个MP4文件总时长: {sum_sound} seconds")
    return sum_sound


def cntnums(directory):
    data=os.walk(directory)
    try:
        # sum_sound=0
        mp4_nums=0
        for file_path,folder,files in data:
            # print(file_path)
            # print(folder)
            # print(files)
            # print('-'*20)
        
                for file in files:
                    
                    if file.endswith('.mp4'):
                        mp4_nums+=1
                        # full_path = os.path.join(file_path, file)
                        # duration = count_mp4_duration(full_path)
                        # print(f" - {full_path}:{duration} seconds")
                        # sum_sound += duration
                    else:continue
    except Exception :
        print("——"*40)
    else :print("——"*40) 
    # print(f"该文件夹下的{mp4_nums}个MP4文件总时长: {sum_sound} seconds")
    return mp4_nums

if __name__=="__main__":
    # directory = input("请输入文件夹路径：")
    # total_duration = cnttime(directory)
    # print(f"该文件夹下的MP4文件总时长: {total_duration} seconds")
    # total_nums=cntnums(directory)
    # print(f"该文件夹下的MP4文件总数量: {total_nums}")
    directory = r"E:\Videos"
    data=os.walk(directory)
    for i in data:
        print(i)
