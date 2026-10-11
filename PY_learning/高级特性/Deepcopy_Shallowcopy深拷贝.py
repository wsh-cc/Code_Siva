"""
https://blog.csdn.net/qq_53031334/article/details/127498301?ops_request_misc=elastic_search_misc&request_id=fec01761a96deb400a2b2d81ce66cc48&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~ElasticSearch~search_v2-2-127498301-null-null.142^v102^control&utm_term=%E6%B7%B1%E6%8B%B7%E8%B4%9D%2F%E6%B5%85%E6%8B%B7%E8%B4%9Dpython&spm=1018.2226.3001.4187
import copy

"""
import copy
pp=['!']
a=[1,2,[1,2,3,4],['赵云','吕布'],pp]
b=a
c=copy.copy(a)
d=copy.deepcopy(a)
print(f'{a}\n,{b}\n,{c}\n,{d}')
print()
a.pop(4)
print(f'{a}\n,{b}\n,{c}\n,{d}')
print()
a[2].pop(2)
print(f'{a}\n,{b}\n,{c}\n,{d}')