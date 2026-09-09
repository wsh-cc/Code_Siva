# import matplotlib.pyplot as plt

# labels='frogs' ,'hogs','dogs','logs'
# sizes=15,20,45,10    
# colors='yellowgreen','gold','lightskyblue','lightcoral'
# explode=0,0.1,0,0
# plt.pie(sizes , explode=explode , labels=labels , colors=colors ,
# autopct='%1.1f%%',shadow=True,startangle=50)
# plt.show()
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D   # 三维图需要

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


# （1）散点图：星空散点图
np.random.seed(7)
x = np.random.randn(120)
y = np.random.randn(120)
size = np.random.randint(20, 120, 120)

plt.figure(figsize=(7, 5))
plt.scatter(x, y, s=size, c=size, cmap='plasma', alpha=0.75)
plt.title("（1）散点图：随机星云")
plt.xlabel("X 坐标")
plt.ylabel("Y 坐标")
plt.grid(alpha=0.3)
plt.show()


# （2）折线图：城市温度变化
days = np.arange(1, 16)
temp = [20, 21, 23, 22, 25, 27, 28, 26, 29, 31, 30, 32, 33, 31, 34]

plt.figure(figsize=(7, 5))
plt.plot(days, temp, marker='o', linewidth=2)
plt.title("（2）折线图：15天温度变化")
plt.xlabel("日期")
plt.ylabel("温度 / ℃")
plt.grid(alpha=0.3)
plt.show()


# （3）函数图：波纹函数
x = np.linspace(-10, 10, 600)
y = np.sin(x) * np.cos(x / 2)

plt.figure(figsize=(7, 5))
plt.plot(x, y, linewidth=2)
plt.title("（3）函数图：y = sin(x)cos(x/2)")
plt.xlabel("x")
plt.ylabel("y")
plt.grid(alpha=0.3)
plt.show()


# （4）添加图例：三种函数对比
x = np.linspace(0, 10, 400)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.sin(x) + np.cos(x)

plt.figure(figsize=(7, 5))
plt.plot(x, y1, label="sin(x)", linewidth=2)
plt.plot(x, y2, label="cos(x)", linewidth=2)
plt.plot(x, y3, label="sin(x)+cos(x)", linewidth=2)

plt.title("（4）添加图例：函数对比图")
plt.xlabel("x")
plt.ylabel("函数值")
plt.legend()
plt.grid(alpha=0.3)
plt.show()


# （5）气泡图：学习时间、成绩、效率
study_time = np.array([1, 2, 3, 4, 5, 6, 7, 8])
score = np.array([55, 60, 66, 72, 78, 83, 88, 92])
efficiency = np.array([100, 180, 260, 350, 460, 580, 720, 900])

plt.figure(figsize=(7, 5))
plt.scatter(study_time, score, s=efficiency, alpha=0.6, c=score, cmap='viridis')
plt.title("（5）气泡图：学习时间与成绩关系")
plt.xlabel("学习时间 / 小时")
plt.ylabel("成绩")
plt.colorbar(label="成绩高低")
plt.grid(alpha=0.3)
plt.show()


# （6）三维曲线：螺旋上升曲线
t = np.linspace(0, 8 * np.pi, 600)
x = np.cos(t)
y = np.sin(t)
z = t

fig = plt.figure(figsize=(7, 5))
ax = fig.add_subplot(111, projection='3d')

ax.plot(x, y, z, linewidth=2)
ax.set_title("（6）三维曲线：螺旋上升曲线")
ax.set_xlabel("X轴")
ax.set_ylabel("Y轴")
ax.set_zlabel("Z轴")

plt.show()