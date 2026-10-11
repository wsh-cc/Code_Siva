# 什么是json
// JSON（JavaScript Object Notation）是一种轻量级的数据交换格式，易于人阅读和编写，同时也易于机器解析和生成。它基于JavaScript的对象表示法，但独立于编程语言，可以在多种语言中使用。
//json模块：可以使得json与python相互转换

# json格式的作用
//为了方便不同语言之间的数据交换，每种语言都可以转换为json格式，进行数据交换

# python数据类型与json格式的相互转换
数据类型->json  叫序列化
json->数据类型  叫反序列化
## json 转 python
res=json.dumps(data)  
res=json.dumps(data,ensure_ascii=False)  // 将python数据类型转换为json格式字符串，且不使用ascii编码,以便正确显示中文字符。
## python 转 json
data = json.loads(res)
###默认只支持dict、list、tuple、str、int、float、bool和None等基本数据类型的转换，如果需要转换其他类型的数据，需要自定义转换函数JSONEncoder。

https://blog.csdn.net/m0_74412436/article/details/141856028?ops_request_misc=elastic_search_misc&request_id=39b0d8b117c6866718c306434a1f5a53&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_click~default-2-141856028-null-null.142^v102^control&utm_term=json&spm=1018.2226.3001.4187

