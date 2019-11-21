#头条移动端信息
import requests
import json
import time
import random
from zlib import crc32
import base64
import re

deviceId = 34960436458
min_behot_times = {}
cookies = {"tt_webid" :"36385357187", 'csrftoken':'7de2dd812d513441f85cf8272f015ce5', '__tasessionId' : '4p6q77g6q1479458262778', 'uuid':"\"w:f2e0e469165542f8a3960f67cb354026\""}

headers ={ "Cache-Control" : "0",
            "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.108 Safari/537.36 2345Explorer/8.0.0.13547",
            "Upgrade-Insecure-Requests" : "1",
            "X-Requested-With" : "XMLHttpRequest",
            'Cache-Control': 'max-age=0'}

def currentSeconds():
    t = int(time.time())
    return t

def getMinBehotTime(category):
    global min_behot_times
    if (category in min_behot_times):
        return min_behot_times[category]
    else:
        min_behot_times[category] = currentSeconds()
        return min_behot_times[category]

def setMinBehotTime(category, seconds):
    global min_behot_times
    min_behot_times[category] = seconds

def get_url(category):
    global deviceId
    url = 'http://is.snssdk.com/api/news/feed/v62/?' \
           'refer=1&count=20' \
           '&loc_mode=4&device_id={0}' \
           '&iid=13136511752' \
           '&category={1}' \
           '&min_behot_time={2}' \
           '&last_refresh_sub_entrance_interval={3}'.format(deviceId, category, getMinBehotTime(category), currentSeconds())

    return url

def getValue(jsonStr, key, defValue):
    if (key in jsonStr):
        return jsonStr[key]
    return defValue

def makeRandom(n):
	rs = ''
	for i in range(0,n):
		rs = rs + str(random.randint(0,9))

	return rs

def makeMidVideoUrl(videoid):
    rd = makeRandom(16)
    url = '/video/urls/v/1/toutiao/mp4/{0}?r={1}'.format(videoid, rd)
    crc = str(crc32(url.encode(' utf-8 ')) & 0xffffffff) 
    videourl = 'http://is.snssdk.com{0}&s={1}'.format(url, crc)
    return videourl

def getVideoUrl(mid_url):
    if (mid_url == ""):
        return ""

    resp = requests.get(mid_url, headers = headers, cookies = cookies)
    if (resp.status_code != 200):
        return ""

    content = resp.content
    contentjson = json.loads(content.decode('utf-8'))
    message = contentjson['message']
    if (message != 'success'):
        print("requst video url fail.")
        return ""
    
    data = contentjson['data']
    video_duration = data['video_duration']
    video_list =  data['video_list']
    video_item = video_list['video_1']
    poster_url = data['poster_url']
    video_main_url = video_item['main_url']
    
    print ("video_duration:",video_duration)
    print ("poster_url:",poster_url)

    return base64.b64decode(video_main_url)
    

def handleNewsContent(content):
    print ("------------------------------")
    contentjson = json.loads(content)
    
    title = contentjson['title']
    display_url = contentjson['display_url']
    article_url = contentjson['article_url']
    has_image = getValue(contentjson,'has_image', "False")
    has_m3u8_video = contentjson['has_m3u8_video']
    has_mp4_video = contentjson['has_mp4_video']
    keywords = getValue(contentjson,'keywords', "")
    has_video = contentjson['has_video']
    article_type = contentjson['article_type']
    article_sub_type = contentjson['article_sub_type']
    publish_time = contentjson['publish_time']

    print ("title:",title)
    print ("has_video:", has_video)
    print ("keywords:",keywords)
    print ("has_image:",has_image)
    print ("display_url:",display_url)
    print ("article_url:",article_url)
    print ("article_type:",article_type)
    print ("article_sub_type:",article_sub_type)
    print ("publish_time:",publish_time)

    # 关键字《》
    t = re.findall('\《([^》]+)\》', title)
    moviename = ''.join(t)
    #if(moviename == ''):
    #    t = re.findall('([^：]+)\：', title)
    #    moviename = ''.join(t)
    print('moviename: 《%s》' %moviename)
    
    if (has_video):
        video_id = contentjson['video_id']
        video_style = contentjson['video_style']
        print ("video_id:",video_id)
        print ("video_style:",video_style)
        video_mid_url = makeMidVideoUrl(video_id)
        print ("video_mid_url:", video_mid_url)
        video_url = getVideoUrl(video_mid_url)
        print ("video_url:", video_url)
        


def getNewsDetail(url):
    global cookies
    global headers
    resp = requests.get(url, headers = headers, cookies = cookies)
    if (resp.status_code != 200):
        return
    #print resp.content

    try:
        res = resp.text

        r = re.compile(r"content:(.*?),")
        result = r.findall(res)[0]
        item = []
        cont = re.compile(u'[\u4E00-\u9FA5]+')
        data = cont.findall(result)
        for i in data:
            item.append(i)
        content = ''.join(result)
        print ('content:', content)

        s = re.compile(r"name:(.*?),")
        source = s.findall(res)[0]
        print ('auther:', source)

        t = re.findall('time:(.*)', res)
        time = ''.join(t).encode("utf-8")
        print ('time:', time)
    except Exception as e:
        print (e)
        pass

def printCookies(cookies):
    for h in cookies:
        print(h+" : "+cookies[h] + '\r\n')

def getNewsList(category):
    global cookies
    global headers

    url = get_url(category)
    print (url)
    resp = requests.get(url, headers = headers, cookies = cookies)
    if (resp.status_code != 200):
        return
    print (resp.cookies)
    
    content = resp.content
    jsondata = json.loads(content.decode('utf-8'))
    message = jsondata['message']
    if (message != 'success'):
        return
    datas = jsondata['data']
    hasmore = jsondata['has_more']
    totalnum = jsondata['total_number']

    print (hasmore,totalnum)
    for news in datas:
        content = news['content']
        handleNewsContent(content)

#deviceId = makeRandom(11)
getNewsList('subv_movie')

#getNewsDetail('https://www.toutiao.com/a6715719011641852428/')
