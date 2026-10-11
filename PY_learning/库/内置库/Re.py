#正则表达式:用来匹配字符串中符合特定模式的文本。它是一种强大的工具，可以用于搜索、替换和提取文本中的特定信息。
#正则表达式由普通字符和特殊字符组成，特殊字符具有特定的含义，可以用来定义复杂的匹配模式。
import re
"""
https://blog.csdn.net/julong187/article/details/135586381?ops_request_misc=elastic_search_misc&request_id=b951a8208963b691f17a48d3d3021feb&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~ElasticSearch~search_v2-4-135586381-null-null.142^v102^control&utm_term=python%20re%E6%AD%A3%E5%88%99&spm=1018.2226.3001.4187
"""
#python3 \w匹配中文！
#如果不相匹配中文，加一个re.ASCII
#    print(re.findall("我\w+n。","我爱python。我喜欢正则表达式。", re.ASCII))

text ="我爱python。我喜欢正则表达式。"
res=re.findall("我\w+n。",text)
print(res)