from copy import deepcopy
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['figure.figsize'] = (16, 9)
plt.style.use('ggplot')

# 导入数据集
data = pd.read_csv('xclara.csv')

# 将 csv 文件中的 V1、V2 两列转成二维数组
f1 = data['V1'].values
f2 = data['V2'].values
X = np.array(list(zip(f1, f2)))

# 计算两个坐标点之间的距离
def dist(a, b, ax=1):
    return np.linalg.norm(a - b, axis=ax)

# 设置分类数
k = 3

# 为了结果稳定，设置随机种子
np.random.seed(42)

# 随机选择 k 个样本点作为初始聚类中心
index = np.random.choice(len(X), k, replace=False)
C = X[index].astype(float)

print("初始聚类中心：")
print(C)

# 保存旧的聚类中心
C_old = np.zeros(C.shape)

# 保存每个点所属的类别
clusters = np.zeros(len(X), dtype=int)

# 计算新旧中心点之间的距离
iteration_flag = dist(C, C_old)

tmp = 1

# K-Means 聚类
while iteration_flag.any() != 0 and tmp < 20:
    # 计算每个点到各个中心点的距离，并归类到最近的中心
    for i in range(len(X)):
        distances = dist(X[i], C)
        cluster = np.argmin(distances)
        clusters[i] = cluster

    # 保存当前中心点
    C_old = deepcopy(C)

    # 重新计算每一类的中心点
    for i in range(k):
        points = X[clusters == i]

        # 防止某一类没有数据点
        if len(points) > 0:
            C[i] = np.mean(points, axis=0)

    # 计算中心点是否还在变化
    iteration_flag = dist(C, C_old)

    tmp += 1

print("最终聚类中心：")
print(C)
print("迭代次数：", tmp)

# 绘制聚类结果
colors = ['red', 'green', 'blue']

for i in range(k):
    points = X[clusters == i]
    plt.scatter(points[:, 0], points[:, 1], s=40, c=colors[i], label=f'第{i + 1}类')

# 绘制聚类中心
plt.scatter(C[:, 0], C[:, 1], s=250, c='black', marker='*', label='聚类中心')

plt.title('K-Means 聚类结果')
plt.xlabel('V1')
plt.ylabel('V2')
plt.legend()
plt.grid(True)
plt.show()