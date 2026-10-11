"""
新增一笔：收入/支出、金额、分类、账户、时间、备注
删除一笔：按 id/按条件删除
修改一笔：改金额/分类/备注等
查询/列表：按日期范围、分类、关键词、账户筛选
统计汇总：
本月收入/支出/结余
按分类汇总（餐饮/交通…）
按日/周/月趋势
预算：每月预算、分类预算、超支提醒
导入/导出：JSON/CSV（便于备份、Excel 查看）

"""
from logger import logger
from storage import save_data,load_data

def add_record(type, amount, category, account, date, note):
   try:
         record={
              "ID":len(load_data())+1,
              "type":type,
              "amount":amount,
              "category":category,
              "account":account,
              "date":date,
              "note":note
         }
         datas=load_data()
         datas.append(record)
         save_data(datas)
         logger.info(f"add a record : {record}")
   except Exception as e:
            logger.error(f"failed to add a record : {e}")
            raise e

def remove_record(id):
    try:
        datas=load_data()
        datas=[data for data in datas if data['ID']!=id]
        save_data(datas)
        logger.info(f'remove a record with id : {id}')
    except Exception as e:
        logger.error(f"failed to remove a record : {e}")
        raise e
    
def update_record(id,**kwargs):
    try:
        datas=load_data()
        for data in datas:
            if data['ID']==id:
                for k,v in kwargs.items():
                    if v is not None and v != "":
                        data[k]=v
        save_data(datas)
        logger.info(f"update a record with id : {id}")
    except Exception as e:
        logger.error(f"failed to update a record : {e}")
        raise e
    
def check_all_records():
    try:
        datas=load_data()
        for data in datas:
            print(f"_$_ : {data}")
        logger.info(f"check all records")
    except Exception as e:
        logger.error(f"failed to check records : {e}")
        raise e

# def query_records(**kwargs):
#     #start_date,end_date,category,account,keyword
#     datas=load_data()
    
