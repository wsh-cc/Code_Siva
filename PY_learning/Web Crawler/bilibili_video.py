"""
bilibili 的视频是画面和声音分开的，所以需要下载两段视频，然后用MoviePy库合并成一个视频

"""
import requests
from package.SAVEPATH import save_path_inDownload
url1 ="https://cn-jstz-cu-01-03.bilivideo.com/upgcxcode/00/94/37618059400/37618059400-1-30016.m4s?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M=&platform=pc&oi=2073291812&gen=playurlv3&os=bcache&nbs=1&uipk=5&trid=0000f83ab1f5ea524e1bb37e98277d00eddu&mid=0&deadline=1776590143&og=cos&upsig=bae18ce264cff4b7bce4fd83dc9dc3d9&uparams=e,platform,oi,gen,os,nbs,uipk,trid,mid,deadline,og&cdnid=71703&bvc=vod&nettype=0&bw=626100&lrs=100&dl=0&f=u_0_0&qn_dyeid=966950b32ef34190004d2a7669e4811f&agrr=1&buvid=B6DA0A23-FA08-C375-B745-9475156DAC7470052infoc&build=0&orderid=0,3"

url2="https://xy116x207x130x228xy.mcdn.bilivideo.cn:8082/v1/resource/upgcxcode/00/94/37618059400/37618059400-1-30216.m4s?agrr=1&build=0&buvid=B6DA0A23-FA08-C375-B745-9475156DAC7470052infoc&bvc=vod&bw=65740&cdnid=71702&deadline=1776590143&dl=0&e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfqXBvEqxTEto8BTrNvN0GvT90W5JZMkX_YN0MvXg8gNEV4NC8xNEV4N03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B5tZlqNCNEto8BTrNvNC7MTX502C8f2jmMQJ6mqF2fka1mqx6gqj0eN0B599M%3D&f=u_0_0&gen=playurlv3&lrs=100&mid=0&nbs=1&nettype=0&og=hw&oi=2073291812&orderid=0%2C3&os=bcache&platform=pc&qn_dyeid=966950b32ef34190004d2a7669e4811f&sign=815c07&traceid=trmkVWYmqaZIAf_0_e_N&uipk=5&uparams=e%2Coi%2Cuipk%2Cgen%2Cmid%2Cdeadline%2Cnbs%2Cplatform%2Cos%2Cog%2Ctrid&upsig=4ed09f77f632c0d266da530b21ed77ea"

headers = {
   "Referer":"https://www.bilibili.com/video/BV1wYdWB5EVF/?spm_id_from=333.934.0.0",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
    "Cookies" :"theme-tip-show=SHOWED; _uuid=9D10C8FBB-C210F-16E1-5C63-5AA21FE8C19D39174infoc; CURRENT_QUALITY=0; buvid3=B6DA0A23-FA08-C375-B745-9475156DAC7470052infoc; b_nut=1760079070; buvid_fp=209732c2a69c3aaf17a3b676efaca5d8; buvid4=5CFCBFC1-8773-19F5-3807-0C553F56112471061-025101014-w7xIbT5KbcspT3xGYxBc/g%3D%3D; bsource=search_bing; home_feed_column=5; browser_resolution=1699-945; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzY4NDEzNjksImlhdCI6MTc3NjU4MjEwOSwicGx0IjotMX0.nG_zrvDyViulJXogEQ7tfYIC4vz0jg9hU6mbaWqSiDA; bili_ticket_expires=1776841309; sid=8cqmbajo; rpdid=|(k|~Jkmu)uk0J'u~~Yl)ku~m; CURRENT_FNVAL=4048; b_lsid=F5B3E2F8_19DA49BE07B" 
}

reponse1 = requests.get(url1,headers=headers)
reponse2 = requests.get(url2,headers=headers)

with open(save_path_inDownload("video1.mp4"), "wb") as f:
    f.write(reponse1.content)

with open(save_path_inDownload("video2.mp4"), "wb") as f:
    f.write(reponse2.content)

#下载成功了，那么怎么合并视频呢，用MoviePy库
"""我 注 释 掉 了"""
# from moviepy import ffmpeg_tools
# ffmpeg_tools.ffmpeg_merge_video_audio(save_path_inDownload("video1.mp4"), save_path_inDownload("video2.mp4"), save_path_inDownload("Lv.999银狼.mp4"))

