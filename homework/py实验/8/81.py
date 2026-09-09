import os
import csv

# 一、os模块操作目录和文件
p = "abc"

# 创建目录
if not os.path.exists(p):
    os.mkdir(p)

# 创建几个子目录
for name in ["a", "b", "c"]:
    path = os.path.join(p, name)
    if not os.path.exists(path):
        os.mkdir(path)

print("目录创建完成")


# 二、txt文件的写入
txt1 = os.path.join(p, "a", "1.txt")
txt2 = os.path.join(p, "b", "2.txt")
txt3 = os.path.join(p, "c", "3.txt")

f = open(txt1, "w", encoding="utf-8")
f.write("我爱中国\n")
f.write("今天学习Python文件操作\n")
f.write("中国发展很快\n")
f.close()

f = open(txt2, "w", encoding="utf-8")
f.write("这是一个普通文本文件\n")
f.write("里面没有关键词\n")
f.close()

f = open(txt3, "w", encoding="utf-8")
f.write("中国文化源远流长\n")
f.write("文件读写是Python的重要内容\n")
f.close()

print("txt文件写入完成")


# 三、读取txt文件，并统计含有“中国”的文件和行号
count = 0

for root, dirs, files in os.walk(p):
    # 跳过Jupyter自动生成的备份目录
    dirs[:] = [d for d in dirs if d != ".ipynb_checkpoints"]

    for file in files:
        if file.endswith(".txt"):
            txt_path = os.path.join(root, file)
            line_nums = []

            try:
                f = open(txt_path, "r", encoding="utf-8")
                lines = f.readlines()
                f.close()

                for i in range(len(lines)):
                    if "中国" in lines[i]:
                        line_nums.append(i + 1)

                if line_nums:
                    count += 1
                    print("文件名：", txt_path)
                    print("含有“中国”的行号：", *line_nums)

            except:
                print(txt_path, "读取失败")

print("含有“中国”的txt文件数量为：", count)


# 四、csv文件的写入
csv_file = "student.csv"

header = ["学号", "姓名", "性别", "年龄", "成绩"]
rows = [
    ["1001", "Jack", "男", 20, 88],
    ["1002", "Rose", "女", 19, 92],
    ["1003", "Tom", "男", 21, 76],
    ["1004", "Lucy", "女", 20, 95]
]

try:
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        fw = csv.writer(f)
        fw.writerow(header)
        fw.writerows(rows)
    print("csv文件写入成功")
except:
    print("csv文件写入失败")


# 五、csv文件的读取
try:
    with open(csv_file, "r", encoding="utf-8-sig") as f:
        fr = csv.reader(f)
        data = [row for row in fr]

    print("csv文件读取结果：")
    for row in data:
        print(row)

    print("表头：", data[0])
    print("第一行数据：", data[1])

except:
    print("csv文件读取失败")