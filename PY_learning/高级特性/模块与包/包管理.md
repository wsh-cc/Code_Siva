import导入、自定义模块、包管理、虚拟环境venv


import 导入
https://blog.csdn.net/2301_79556402/article/details/149880156?ops_request_misc=&request_id=&biz_id=102&utm_term=import&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduweb~default-0-149880156.142^v102^control&spm=1018.2226.3001.4187

自定义模块

https://blog.csdn.net/2501_94051735/article/details/155541539?ops_request_misc=elastic_search_misc&request_id=72b857cf98a2704d6f975d98d95701d4&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~baidu_landing_v2~default-5-155541539-null-null.142^v102^control&utm_term=python%E8%87%AA%E5%AE%9A%E4%B9%89%E6%A8%A1%E5%9D%97&spm=1018.2226.3001.4187

包管理

https://blog.csdn.net/weixin_46375180/article/details/142835293?ops_request_misc=elastic_search_misc&request_id=94ee29c8e4de4b1aed1a266e6bad2d1d&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-142835293-null-null.142^v102^control&utm_term=pip%E6%93%8D%E4%BD%9C&spm=1018.2226.3001.4187

Python包管理（后端基础）
1️⃣ 什么是包管理
管理第三方库（安装 / 更新 / 删除）
解决项目依赖问题
2️⃣ 核心工具
pip：安装和管理Python库
venv：创建虚拟环境（隔离不同项目）//目前不知道怎么隐藏

3️⃣ 常用命令
pip install 包名          # 安装
pip uninstall 包名        # 卸载
pip list                 # 查看已安装
pip install --upgrade 包名  # 更新

4️⃣ 依赖管理（重点）
pip freeze > requirements.txt     # 导出当前依赖
pip install -r requirements.txt   # 安装所有依赖

5️⃣ 虚拟环境
python -m venv venv     # 创建虚拟环境

# 激活
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux

# 退出虚拟环境
deactivate              # 退出虚拟环境
6️⃣ 一句话总结

👉 包管理 = pip + 虚拟环境 + requirements.txt
