"""
import time
from threading import Thread
 
COUNT = 200_000_000
 
def countdown():
    n = COUNT
    while n > 0:
        n -= 1
 
# --- 单线程测试 ---
start_time = time.time()
countdown()
countdown()
end_time = time.time()
print(f"单线程耗时: {end_time - start_time:.4f} 秒")
 
# --- 双线程测试 ---
thread1 = Thread(target=countdown)
thread2 = Thread(target=countdown)
start_time = time.time()
thread1.start()
thread2.start()
thread1.join()
thread2.join()
end_time = time.time()
print(f"双线程耗时: {end_time - start_time:.4f} 秒")
"""
# 很明显的案例GIL
import requests
import time
from threading import Thread

def fetch_url(url, idx=None):
    try:
        r = requests.get(url, timeout=5)   # 加超时
        print(f"[{idx or ''} status={r.status_code}]")
    except Exception as e:
        print(f"{idx or ''} error:", e)

def main():
    urls = ["https://www.baidu.com/"] * 10

    # 单线程
    start = time.time()
    for i, url in enumerate(urls, 1):
        fetch_url(url, i)
    print(f"单线程耗时: {time.time() - start:.4f} 秒")

    # 多线程 对访问网络IO密集型任务，GIL不影响性能，如访问网站
    start = time.time()
    threads = [Thread(target=fetch_url, args=(url, i)) for i, url in enumerate(urls, 1)]
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"多线程耗时: {time.time() - start:.4f} 秒")

if __name__ == "__main__":
    main()
# ...existing code...