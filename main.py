#
#create on 2019-8-27
#
from geting_toutiao_m import geter
from loger import loger
import datetime
import threading
import sys
import re
import time
import logging

next_end_time = 0
end_state = False
lists = []

class Runtime:
    def __init__(self,starttime,endtime):
        self.starttime = starttime
        self.endtime = endtime
    def __repr__(self):
        return repr((self.starttime,self.endtime))

def check_argu():
    global lists
    lists1 = sorted(lists, key=lambda runtime: int(runtime.endtime))
    
    #结束时间不能小于开始时间
    for m in lists:
        if(m.endtime <= m.starttime):
            print("endtime <= starttime,Please check the!")
            return -1
    
    #开始和结束时间排序，顺序要一致
    if(lists != lists1):
        print("Argument error ,Please check the!")
        return -1

    #上一次结束时间不能大于下一次开始时间
    i = 0
    while ((i+1)<len(lists)):
        if(lists[i].endtime >= lists[i+1].starttime):
            print("last endtime({0}) > next starttime({0}),Please check the!".format(lists[i].endtime,lists[i+1].starttime))
            return -1
        i += 1
    
    return 0

def init(argu):
    i = 0
    global lists
    for n in argu:
        if(i == 0):
            i += 1
            continue
        t = re.findall('\[([^]]+)\]', argu[i])
        argument = ''.join(t)
        str1, str2 = argument.split(',')
        print('argument: %s or %s' %(str1, str2))
        lists.append(Runtime(str1, str2))
        i += 1
    
    #排序
    lists = sorted(lists, key=lambda runtime: int(runtime.starttime))
    logging.info("timelist:{0}".format(lists))
    #检查参数是否正确
    if(check_argu() != 0): return -1
    return 0

def get_time():
    # 获取现在时间
    now_time = datetime.datetime.now()
    next_start_hour = '0'
    next_end_hour = '0'
    global lists
    for n in lists:
        #获取合适的时间
        if(int(n.starttime) >= 24):
            lists.remove(n)
            continue
        if(now_time.time().hour <= int(n.starttime)):
            #选择合适中最小的时间，排序好了就不需要了
            #if((int(n.starttime) < int(next_start_hour))|(next_start_hour == '0')):
            next_start_hour = n.starttime
            next_end_hour = n.endtime
            #合适就删除
            lists.remove(n)
            break
    else:
        logging.error('Please,Give me the right time !')
        return -1
    #next_time = 0
    #if((int(next_end_hour) >= 24)):
    #    # 获取明天时间
    #    next_time = now_time + datetime.timedelta(days=+1)
    #    next_end_hour = int(next_end_hour) - 24
    #else:
    #    next_time = now_time
    next_time = now_time
    next_year = next_time.date().year
    next_month = next_time.date().month
    next_day = next_time.date().day
    #获取下一次运行时间和结束的时间
    global next_end_time
    next_start_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" {0}:36:00".format(next_start_hour), "%Y-%m-%d %H:%M:%S")
    next_end_time = datetime.datetime.strptime(str(next_year)+"-"+str(next_month)+"-"+str(next_day)+" {0}:00:00".format(next_end_hour), "%Y-%m-%d %H:%M:%S")
    
    # 获取距离下一次时间，单位为秒
    timer_start_time = (next_start_time - now_time).total_seconds()
    #timer_end_time = (next_end_time - now_time).total_seconds()
    logging.info("hour:{0}----start:{1}----end:{2}".format(next_start_hour, next_start_time, next_end_time))
    return timer_start_time

def end():
    global end_state
    end_state = True
    
    #睡眠足够久，保证上次爬取退出
    while (end_state):
        time.sleep(5)
        
    next_time = get_time()
    if(next_time < 0):
        logging.info("code quit !!")
        return
    logging.info("next_time start {0} end_state{1}".format(next_time,end_state))
    timer = threading.Timer(next_time, main)
    timer.start()
    logging.info("end exit !!")

def main():
    global next_end_time,end_state
    # 获取现在时间,计算结束的时间
    now_time = datetime.datetime.now()
    timer_end_time = (next_end_time - now_time).total_seconds()
    logging.info("timer_end_time start {0} end_state{1}".format(timer_end_time,end_state))
    
    timer = threading.Timer(timer_end_time, end)
    timer.start()
    geting = geter()
    while (not end_state):
        geting.getNewsList('subv_movie')
    
    end_state = False
    logging.info("main exit")

if __name__ == "__main__":
    loging = loger()
    count = len(sys.argv)
    if (count < 2):
        next_start_time = datetime.datetime.strptime(str(2019)+"-"+str(8)+"-"+str(30)+" {0}:00:00".format(0), "%Y-%m-%d %H:%M:%S")
        logging.error('Please,Give one argument!')
    else:
        if(init(sys.argv) == 0):
            next_time = get_time()
            print(lists)
            if(next_time >= 0):
                #定时器,参数为(多少时间后执行，单位为秒，执行的方法)
                timer = threading.Timer(next_time, main)
                timer.start()