"""
爬虫思路
一、数据来源分析
    1、爬什么
        B站视频(静态也在源代码中)及标题
    2、去哪儿爬
        判断动静态
            静态 ==> 我在源代码里搜索标题，发现有json格式的数据 ==> json在script标签中
        url
            "https://www.bilibili.com/video/BV1b24y1F7b7/?vd_source=a07c30f4390351f91457163f676b47ca"
二、代码实现
    1、发送请求
    2、获取数据
    3、解析数据
    4、保存数据

"""
import requests
import re
import json
import os  #系统模块，让Python操作我的系统

def get_html(url,headers):
    try:
        resp = requests.get(url=url, headers=headers)
        resp.encoding = 'utf-8'
        resp.raise_for_status()  # 自动触发崩溃
        return resp.text
    except:
        return ''


def parse_html(html):
    """
    解析数据的集中方法：
    1、解析（string-->object）
        json、xpath
    2、搜索（re正则）
        re
    """
    js_code = re.findall(r'<script>window.__playinfo__=(.*?)</script>', html, re.S)[0]  #（匹配规则，字符串，flags）
    # r禁止转义、re.S搜索所以字符串包括换行符
    # .匹配任意字符但不包括换行符
    # *匹配出现0或无数次，作用于前一个匹配符
    # *?匹配到想要的结果后就停止， ?匹配0或一次
    json_dict = json.loads(js_code)  # 将json字符串转为Python字典
    #解析视频url
    data = json_dict['data']
    dash = data['dash']
    video = dash['video']
    #解析视频url
    audio = dash['audio']
    video_base_url = video[0]['base_url']
    audio_base_url = audio[0]['base_url']
    # 解析标题
    title = re.findall(r'<title.*?>(.*?)</title>', html, re.S)[0]
    data_dict = {
        'title': title,
        'video_base_url': video_base_url,
        'audio_base_url': audio_base_url,
    }
    return data_dict

def save_data(data, headers):
    # 如果没有文件夹我就创建一个
    base_filename = './视频/'
    """
        功能：判断一个文件夹存在与否
        参数：文件夹路径、
        返回值：无
    """
    # 创建主文件夹
    if not os.path.exists(base_filename):
        os.mkdir(base_filename)
        """
        功能：新建一个文件夹
        参数：路径
        返回值；无
        """

    # 发送请求获取数据
    video = get_content(url=data['video_base_url'], headers=headers)
    audio = get_content(url=data['audio_base_url'], headers=headers)

    # 创建目标视频文件夹
    filename = base_filename + f'{data["title"]}/'
    if not os.path.exists(filename):
        os.mkdir(filename)

    with open(filename + 'video.mp4', 'wb') as f:
        f.write(video)

    with open(filename + 'audio.mp3', 'wb') as f:
        f.write(audio)

    combine(filename)

def combine(filename):
    # os.system
    """
    功能：让Python执行cmd命令
    参数：命令字符串
    返回：无
    """
    os.system(f'ffmpeg -i {filename}video.mp4 -i {filename}audio.mp3 -c:v copy -c:a aac -strict experimental {filename}output.mp4')



def get_content(url, headers):
    try:
        resp = requests.get(url=url, headers=headers)
        resp.raise_for_status()

        return resp.content  # 二进制数据，text文本数据，json()json数据
    except:
        return None



def main():
    url = "https://www.bilibili.com/video/BV1b24y1F7b7/"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58',
        'referer': 'https://www.bilibili.com/',
    }
    html = get_html(url, headers)
    # print(html[:1000])
    if not html:
        print('获取失败')

    data = parse_html(html)

    if not data:
        print('解析失败')

    save_data(data, headers)


if __name__ == '__main__':
    main()