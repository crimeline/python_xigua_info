#头条PC端信息
import requests
import json
import time
import math
import hashlib
import re
import time

def getASCP():
    t = int(math.floor(time.time()))
    e = hex(t).upper()[2:]
    m = hashlib.md5()
    m.update(str(t).encode(encoding='utf-8'))
    i = m.hexdigest().upper()

    if len(e) != 8:
        AS = '479BB4B7254C150'
        CP = '7E0AC8874BB0985'
        return AS,CP

    n = i[0:5]
    a = i[-5:]
    s = ''
    r = ''
    for o in range(5):
        s += n[o] + e[o]
        r += e[o + 3] + a[o]

    AS = 'A1' + s + e[-3:]
    CP = e[0:3] + r + 'E1'
    print("AS:"+AS,"CP:"+CP)
    return AS,CP



def get_url(max_behot_time,AS,CP):
    url = 'https://www.toutiao.com/api/pc/feed/?category=news_hot&utm_source=toutiao&widen=1' \
           '&max_behot_time={0}' \
           '&max_behot_time_tmp={0}' \
           '&tadrequire=true' \
           '&as={1}' \
           '&cp={2}'.format(max_behot_time,AS,CP)
    print(url)
    return url

tt_webid = ""

def get_item(url):
    global tt_webid
    headers = {'user-agent':"Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Mobile Safari/537.36"}
    cookies = {"tt_webid":tt_webid}
    #wbdata = requests.get(url,cookies = cookies).content
    resp = requests.get(url, headers = headers, cookies = cookies)
    wbdata = resp.content
    #print wbdata
    wbdata2 = json.loads(wbdata.decode('utf-8'))
    if wbdata2['message'] == 'error':
        return 0

    tt_webid = resp.cookies['tt_webid']
    #print resp.cookies
    #print tt_webid

    data = wbdata2['data']
    for news in data:
        title = news['title']
        news_url = news['source_url']
        news_url = "https://www.toutiao.com"+news_url

        print(title,news_url)
        getNewsDetail(news_url)
        time.sleep(2)
    next_data = wbdata2['next']
    next_max_behot_time = next_data['max_behot_time']
    #print("next_max_behot_time:{0}".format(next_max_behot_time))
    return next_max_behot_time

#写文件
def writer(filename, content, source, time, tags):
    write_flag = True
    with open(filename, 'a', encoding='utf-8') as f:
        f.write('内容：'+'\n')
        f.writelines(content)
        f.write('\n\n')
        f.write('作者：'+source + '\n')
        f.write('时间：'+time + '\n')
        f.write('标签：'+tags + '\n')
        f.write('------------------------分割线------------------------'+'\n\n')

def getNewsDetail(url):
    global tt_webid
    
    headers ={ "Cache-Control" : "0",
            "User-Agent" : "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.108 Safari/537.36 2345Explorer/8.0.0.13547",
            "Upgrade-Insecure-Requests" : "1",
            "X-Requested-With" : "XMLHttpRequest"}

    cookies = {"tt_webid":tt_webid}
    '''获取详情内容、发帖人、时间'''
    response = requests.get(url, headers=headers, cookies = cookies)
    if (response.status_code != 200):
        return
    try:
        res = response.text
        # 内容
        r = re.compile(r"content:(.*?),")
        result = r.findall(res)[0]
        #item = []
        #cont = re.compile(u'[\u4e00-\u9fa5a-zA-Z0-9]+')#[\u4E00-\u9FA5] [a-zA-Z0-9\u4e00-\u9fa5]
        #data = cont.findall(result)
        #for i in data:
        #    item.append(i)
        #content = ''.join(item)
        content = ''.join(result)
        print('content: ', content)
        # 作者
        s = re.compile(r"name:(.*?),")
        source = s.findall(res)[0]
        print('source: %s' %source)
        # 时间
        t = re.findall('time:(.*)', res)
        time = ''.join(t)
        print('time: %s' %time)
        #tags
        s = re.compile(r"tags:(.*?)],")
        tags = s.findall(res)[0]
        print('source: %s' %tags)
        writer("aaa.txt", content, source, time, tags)
    except Exception as e:
        print('Exception error !!!')
        pass

refresh = 1
for x in range(0,refresh+1):
    print("{0}".format(x))
    if x == 0:
        max_behot_time = 0
    else:
        max_behot_time = next_max_behot_time
        print (max_behot_time)

    AS,CP = getASCP()
    url = get_url(max_behot_time,AS,CP)
    next_max_behot_time = get_item(url)

