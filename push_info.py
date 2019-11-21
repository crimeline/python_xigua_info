#对接后台数据api
import requests
import json
import time
from loger import loger
import logging

class pusher:
    def __init__(self):
        self.path="http://112.74.68.252:9800/mcp/api/content_inject"
        self.headers  = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTHL, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        }
        self.log_on_off = False
        self.log_filename = "error_log_{0}.txt"
        self.err_count = 0

    #可选 userPicUrl、userAuthInfo、description
    def get_url(self,userId,userName,userPicUrl,userAuthInfo,contentId,title,category, \
                            videoUrl,coverUrl,duration,keyWord,description,createTime,source):
        url = 'http://112.74.68.252:9800/mcp/api/content_inject?' \
               '&userId={0}' \
               '&userName={1}' \
               '&userPicUrl={2}' \
               '&userAuthInfo={3}' \
               '&contentId={4}' \
               '&title={5}' \
               '&category={6}' \
               '&videoUrl={7}' \
               '&coverUrl={8}' \
               '&duration={9}' \
               '&keyWord={10}' \
               '&description={11}' \
               '&createTime={12}' \
               '&source={13}'.format(userId,userName,userPicUrl,userAuthInfo,contentId,title,category,videoUrl,coverUrl,duration,keyWord,description,createTime,source)
        logging.info(url)
        return url
    
    def get_item(self, url):
        headers  = {
            'user-agent':"Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Mobile Safari/537.36"
        }
        resp = requests.get(url, headers  = headers , cookies = '')
        wbdata = resp.content
        wbdata2 = json.loads(wbdata.decode('utf-8'))
        
        if wbdata2['ret'] != '0':
            logging.error('this error: ',wbdata2['retInfo'])
            return -1
        else:
            logging.debug('push successful')
            return 0

    def post_data(self,userId,userName,userPicUrl,userAuthInfo,contentId,title,category, \
                            videoUrl,coverUrl,duration,keyWord,description,createTime,source):
        postdata = {'userId':userId,'userName':userName,'userPicUrl':userPicUrl,'userAuthInfo':userAuthInfo,'contentId':contentId, \
            'title':title,'category':category,'videoUrl':videoUrl,'coverUrl':coverUrl,'duration':duration,'keyWord':keyWord, \
            'description':description,'createTime':createTime,'source':source}
        logging.debug(postdata)
        for key,value in postdata.items():
            logging.info('{key}:{value}'.format(key = key, value = value))
        return postdata

    def post_item(self, postdata):
        try:
            resp=requests.post(self.path, data=postdata)
            wbdata = resp.content
            wbdata2 = json.loads(wbdata.decode('utf-8'))
            if wbdata2['ret'] != '0':
                logging.error('this error: ', wbdata2['retInfo'])
                return -1
            else:
                logging.debug('push successful')
                return 0
        except Exception as e:
            logging.error("post error")
            return -1

    def post_requst(self, postdata):
        ret = self.post_item(postdata)
        if(ret == -1):
            self.err_count += 1
            if(self.err_count >= 3):
                logging.error("count out")
            else:
                self.post_requst(postdata)
            return -1
        return 0

if __name__ == '__main__':
    loging = loger()
    pushing = pusher()
    #url = pushing.get_url("get",'1','2','3','4','5','6','7','test','12','9','10','11','toutiao')
    #pushing.get_item(url)
    post_data = pushing.post_data("post",'1','2','3','4','5','6','7','test','12','9','10','11','toutiao')
    ret = pushing.post_requst(post_data)
    if(ret == -1):
        pushing2 = pusher()
        ret = pushing2.post_requst(post_data)