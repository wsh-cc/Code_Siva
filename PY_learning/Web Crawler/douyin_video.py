import requests
from package.SAVEPATH import save_path_inDownload
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}
url = "https://v26-web-prime.douyinvod.com/video/tos/cn/tos-cn-ve-15c000-ce/osCQIniBAsfEhyJAw012AtuguAiJueA20GBpnw/media-video-hvc1/?a=6383&ch=0&cr=8&dr=0&er=1&lr=default&cd=0%7C0%7C0%7C3&cv=1&br=681&bt=681&cs=4&ds=6&mime_type=video_mp4&qs=0&rc=PGhoNTc6NzdlNGk4ZjkzOUBpM2dsZWw5cjZkOTMzbGkzNUAtYWMwNTZgXjExYTEzMzUxYSNrMGpqMmRjZG9hLS1kLTRzcw%3D%3D&btag=c0000e00030000&cquery=101s_100o&dy_q=1776585688&expire=1776672357&l=20260419160127D0802D34F69420DAE0EA&ply_type=4&policy=4&signature=f4090c15b912976ac7fc0cceebc5301c&tk=webid&webid=c4683e1a43ffa6bc6852097c712d14b81f04bc9b5ca6d30214b0e66b4e3852802750f7e3fcf0b530300287218ebc459e27b4ab23dfa453e434eb5e49eba1e54820c5d75e4e8d14243c53dfcd2413d8ff11e8485f24095e69fd4885f20980a7c0071f396bcf12148341777f95534c765d0f4962e2281a614e141bf226de30082b9c97992b534deb80021a3e5b151e48604e791af622116c5bd759ec0b4ba66063-57248cd51196ffef399990fdd0590a52&fid=ea9bbca14d29ea87b30cd9f03bf96926"
response = requests.get(url, headers = headers)
with open(save_path_inDownload("douyin_video.mp4"), "wb") as f:
    f.write(response.content)
