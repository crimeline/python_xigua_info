#头条移动端信息
import requests
import json
import time
import random
from zlib import crc32
import base64
import re
import time, datetime
import logging

from loger import loger
from push_info import pusher 

class geter:
    def __init__(self):
        self.log_on_off = True
        self.log_filename = "error_log_{0}.txt"
        #self.deviceId = makeRandom(11)
        self.category = 'subv_movie'
        self.deviceId = 34960436458
        self.min_behot_times = {}
        #odin_tt=59a19a14509946cf6200fbbf2a3fcee481e6b6d8ada676d0eff2667565572828d03cf1fb304fb0d7e151edeb2ec6fdb0
        self.cookies = {"tt_webid" :"36385357187", 'csrftoken':'7de2dd812d513441f85cf8272f015ce5', '__tasessionId' : '4p6q77g6q1479458262778', 'uuid':"\"w:f2e0e469165542f8a3960f67cb354026\""}

        self.headers ={ "Cache-Control" : "0",
                "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.108 Safari/537.36 2345Explorer/8.0.0.13547",
                "Upgrade-Insecure-Requests" : "1",
                "X-Requested-With" : "XMLHttpRequest",
                'Cache-Control': 'max-age=0'}

    def currentSeconds(self):
        t = int(time.time())
        return t

    def getMinBehotTime(self, category):
        if (category in self.min_behot_times):
            return self.min_behot_times[category]
        else:
            self.min_behot_times[category] = self.currentSeconds()
            return self.min_behot_times[category]

    def get_url(self, category):
        url = 'http://is.snssdk.com/api/news/feed/v62/?' \
               'refer=1&count=20' \
               '&loc_mode=4&device_id={0}' \
               '&iid=13136511752' \
               '&category={1}' \
               '&min_behot_time={2}' \
               '&last_refresh_sub_entrance_interval={3}'.format(self.deviceId, category, self.getMinBehotTime(category), self.currentSeconds())

        return url

    def getValue(self, jsonStr, key, defValue):
        if (key in jsonStr):
            return jsonStr[key]
        return defValue

    def makeRandom(self, n):
        rs = ''
        for i in range(0,n):
            rs = rs + str(random.randint(0,9))

        return rs

    def makeMidVideoUrl(self, videoid):
        rd = self.makeRandom(16)
        url = '/video/urls/v/1/toutiao/mp4/{0}?r={1}'.format(videoid, rd)
        crc = str(crc32(url.encode(' utf-8 ')) & 0xffffffff) 
        videourl = 'http://is.snssdk.com{0}&s={1}'.format(url, crc)
        return videourl

    def getVideoUrl(self, mid_url):
        if (mid_url == ""):
            return ""

        resp = requests.get(mid_url, headers = self.headers, cookies = self.cookies)
        if (resp.status_code != 200):
            return ""

        content = resp.content
        contentjson = json.loads(content.decode('utf-8'))
        message = contentjson['message']
        if (message != 'success'):
            logging.error("requst video url fail.")
            return ""
        
        data = contentjson['data']
        video_duration = data['video_duration']
        video_list =  data['video_list']
        video_item = video_list['video_1']
        poster_url = data['poster_url']
        video_main_url = video_item['main_url']
        
        logging.info("video_duration:{0}".format(video_duration))
        logging.info("poster_url:{0}".format(poster_url))

        return base64.b64decode(video_main_url)
        

    def handleNewsContent(self, content):
        logging.info("------------------------------")
        contentjson = json.loads(content)
        
        title = contentjson.get('title','')
        display_url = contentjson.get('display_url','')
        article_url = contentjson.get('article_url','')
        has_image = self.getValue(contentjson,'has_image', "False")
        has_m3u8_video = contentjson.get('has_m3u8_video','')
        has_mp4_video = contentjson.get('has_mp4_video','')
        keywords = self.getValue(contentjson,'keywords', "")
        has_video = contentjson.get('has_video','')
        article_type = contentjson.get('article_type','')
        article_sub_type = contentjson.get('article_sub_type','')
        publish_time = contentjson.get('publish_time','')
        abstract = contentjson.get('abstract','')
        
        logging.info("title:{0}".format(title))
        logging.info("has_video:{0}".format(has_video))
        logging.info("keywords:{0}".format(keywords))
        logging.info("has_image:{0}".format(has_image))
        logging.info("display_url:{0}".format(display_url))
        logging.info("article_url:{0}".format(article_url))
        logging.info("article_type:{0}".format(article_type))
        logging.info("article_sub_type:{0}".format(article_sub_type))
        logging.info("publish_time:{0}".format(publish_time))
        
        #用户信息
        user_name = ''
        user_id = ''
        avatar_url = ''
        verified_content = contentjson.get('verified_content','')
        user_info = contentjson.get('user_info','')
        if (user_info != ''):
            user_name = user_info.get('name','')
            user_id = user_info.get('user_id','')
            avatar_url = user_info.get('avatar_url','')
        
        # 关键字《》
        t = re.findall('\《([^》]+)\》', title)
        moviename = ''.join(t)
        #if(moviename == ''):
        #    t = re.findall('([^：]+)\：', title)
        #    moviename = ''.join(t)
        logging.info('moviename: 《%s》' %moviename)
        video_id = ''
        video_duration = ''
        coverUrl = ''
        video_mid_url = ''
        if (has_video):
            video_id = contentjson.get('video_id','')
            video_style = contentjson.get('video_style','')
            video_duration = contentjson.get('video_duration',0)
            
            video_detail_info = contentjson.get('video_detail_info','')
            if (video_detail_info != ''):
                detail_video_large_image = video_detail_info.get('detail_video_large_image','')
                coverUrl = detail_video_large_image.get('url','')
            
            logging.info("video_id:{0}".format(video_id))
            logging.info("video_style:{0}".format(video_style))
            video_mid_url = self.makeMidVideoUrl(video_id)
            logging.info("video_mid_url:{0}".format(video_mid_url))
            video_url = self.getVideoUrl(video_mid_url)
            logging.info("video_url:{0}".format(video_url))
        
        #上传信息 createTime category coverUrl
        timeArray = time.localtime(publish_time)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        pushing = pusher()
        url = pushing.post_data(user_id,user_name,avatar_url,verified_content,video_id,\
                            title,self.conversionCategory(self.category), video_mid_url,coverUrl,video_duration,keywords,abstract,otherStyleTime,"toutiao")
        pushing.post_requst(url)

    def conversionCategory(self, category):
        dates = {'subv_voice': '音乐', 'subv_funny': '搞笑', 'subv_society': '社会', \
            'subv_comedy': '小品', 'subv_life': '生活', 'subv_movie': '影视', \
            'subv_entertainment': '娱乐', 'subv_cute': '呆萌', 'subv_game': '游戏', \
            'subv_boutique': '原创', 'subv_broaden_view': '开眼'}
        return dates.get(category, '未知')

    def printCookies(self, cookies):
        for h in cookies:
            logging.info(h+" : "+cookies[h] + '\r\n')

    def waiter(self, base):
        i = 1
        time_out = random.randint(47,113)
        logging.debug("sleep time : {0}".format(time_out))
        while i < time_out:
            i += 1
            time.sleep(0.1)
        return

    def getNewsList(self, category):
        url = self.get_url(category)
        logging.info(url)
        resp = requests.get(url, headers = self.headers, cookies = self.cookies)
        if (resp.status_code != 200):
            logging.info('requests url error!')
            return
        logging.info(resp.cookies)
        
        self.category = category
        content = resp.content
        jsondata = json.loads(content.decode('utf-8'))
        message = jsondata['message']
        if (message != 'success'):
            logging.error('message not success!')
            return
        datas = jsondata.get('data','')
        hasmore = jsondata.get('has_more','False')
        totalnum = jsondata.get('total_number','0')
        logging.info("hasmore: {0} totalnum: {1}".format(hasmore,totalnum))
        for news in datas:
            content = news['content']
            self.handleNewsContent(content)
            self.waiter(totalnum)
        #随机等待时间
        self.waiter(totalnum)

if __name__ == "__main__":
    loging = loger()
    geting = geter() 
    while True:
        geting.getNewsList('subv_movie')
