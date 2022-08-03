# -*- coding: UTF-8 -*-

import io, requests, sys, re, grequests
import multiprocessing
import threading
from multiprocessing import Process
import time
import copy


def get_time(f):

    def inner(*arg,**kwarg):
        s_time = time.time()
        res = f(*arg,**kwarg)
        e_time = time.time()
        print('耗时：{}秒'.format(e_time - s_time))
        return res
    return inner


def completion():
    # complete the phone number
    numlist = []
    for n in range(0, 10000000):
        middle_num = str(n).zfill(2)
        numlist.append(middle_num)
    print len(numlist)


def completion(head, tail):
    numlist = []
    for n in range(0, 10000000):
        middle_num = str(n).zfill(6)
        numlist.append(head + middle_num + tail)
    print '生成完毕，共'+str(len(numlist))+'条'
    return numlist


def outfile(numlist):
    print '开始写入文件'
    newfile = 'D:\\phone.txt'
    with io.open(newfile, 'w+', encoding='utf-8') as file_obj:
        for num in numlist:
            file_obj.write((num + '\n').decode())
        file_obj.close()


# 判断归属地
def Judlocation(numlist, location, q):
    print '开始判断归属地'
    # 避免乱码
    reload(sys)
    sys.setdefaultencoding('utf-8')
    # 避免越界，备份list
    numlistbak = copy.deepcopy(numlist[:])
    # 使用grequests并行处理出现线程上限问题
    # req_list = [grequests.get('https://www.baifubao.com/callback?cmd=1059&callback=phone&phone=' + str(numlist[n]))
    #     for        n in range(0, 1000000)]
    # req_list = []
    # 防止过多session未关闭
    session = requests.session()
    session.keep_alive = False
    for n in range(0, len(numlist)):
        try:
            # print str(numlistbak[n])
            res = requests.get('https://www.baifubao.com/callback?cmd=1059&callback=phone&phone=' + str(numlistbak[n]),
                               timeout=0.5)
            if (res.text.split("\"")[5] == '0') & (location in res.text):
                continue
            else:
                numlist.remove(numlistbak[n])
        except Exception as E:
            print '出现异常已跳过%s' % E
            pass
    # print '获取响应完成'
    # print numlist
    q.put(numlist)


@get_time
def createnum():
    global arglist
    while True:
        head = raw_input("请输入手机前三位数：")
        if str(head).isdigit() and int(head) // 10 % 10 in [3, 4, 5, 7, 8]:
            break
    while True:
        tail = raw_input("请输入手机后两位数：")
        if str(head).isdigit() and int(tail) in range(00, 99):
            break
    location = raw_input("请输入电话归属地：")
    # 生成号码
    allnum = completion(str(head)[:3], str(tail))
    # 跨线程读取数据
    q = multiprocessing.Queue()
    # 存储所有结果
    result = []
    for i in range(5):  # 开启5个子进程执行fun1函数
        arglist= allnum[(i) * (len(allnum)) / 5:(i + 1) * len(allnum) / 5]
        # print arglist
        p = Process(target=Judlocation, args=(arglist, location, q))  # 实例化进程对象
        p.start()
        result = result + (q.get())
        p.join()

    # for p in process_list:
    #     print '等待子进程'
    #     print q.get()
    #     print len(result)
    #     result = result + (q.get())
    #     p.join()

    # for j in process_list:

    print (len(result))
    outfile(result)


if __name__ == '__main__':
    createnum()
