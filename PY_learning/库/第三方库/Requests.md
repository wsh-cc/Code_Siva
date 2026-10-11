## request方法的第一个参数是请求方法，可以是'get'、'post'等，大小写不敏感。第二个参数是URL，返回一个Response对象。可以通过Response对象的text属性获取响应内容。

CSDN上关于requests库的文章：可以参考一下
https://blog.csdn.net/wly55690/article/details/132201974?ops_request_misc=elastic_search_misc&request_id=823c6e7e6dba2bfe4617fb5db9b9ee35&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~top_positive~default-1-132201974-null-null.142^v102^control&utm_term=requests%E5%BA%93&spm=1018.2226.3001.4187

## request 方法
   r=equests.request('get', 'https://www.baidu.com')
   第一个参数可以为get,post,put,delete等，大小写不敏感
   第二个参数为URL，返回一个Response对象，可以通过Response对象的text属性获取响应内容。
   后面的参数可以是params、data、json、headers等，具体可以参考官方文档：https://docs.python-requests.org/en/latest/api/#requests.request