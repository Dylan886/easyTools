# -*- coding: UTF-8 -*-

import multiprocessing
from multiprocessing import Process
# openpyxl写入文件上限为百万级，而xlwt仅为65535
import openpyxl
import time
from phone import *


def get_time(f):
    def inner(*arg, **kwarg):
        s_time = time.time()
        res = f(*arg, **kwarg)
        e_time = time.time()
        print('耗时：{}秒'.format(e_time - s_time))
        return res

    return inner


def completion(head, tail):
    numlist = []
    for n in range(0, 1000000):
        middle_num = str(n).zfill(6)
        numlist.append(head + middle_num + tail)
    print('生成完毕，共' + str(len(numlist)) + '条')
    return numlist


def outfile(numlist):
    print('开始写入文件')
    outwb = openpyxl.Workbook()  # 创建工作簿
    outws = outwb.create_sheet("手机号码")  # 在工作簿中新建一个工作表new
    outws.append(['手机号码', '姓名'])  # 给新表的第一行添加对应的标签
    for i in numlist:
        outws.append([i, i])   # 给新表的每个列添加对应的数据
    try:
        outwb.save('D:\\phone.xlsx')  # 最后在同目录下生成的文件New_phone.xls
    except Exception as f:
        print(f)
        pass


# 判断归属地
def judlocation(numlist, location, q):
    # 记录符合归属地条件的电话号码
    # 浅拷贝准备删除不合格号码
    numlistbak = numlist.copy()
    for i in numlistbak:
        print(i)
        if Phone().find(int(i))['province'] != location:
            numlist.remove(i)
    # print(numlist)
    q.put(numlist)


@get_time
def createnum():
    global arglist
    while True:
        head = input("请输入手机前三位数：")
        if str(head).isdigit() and int(head) // 10 % 10 in [3, 4, 5, 7, 8]:
            break
    while True:
        tail = input("请输入手机后两位数：")
        if str(head).isdigit() and int(tail) in range(00, 99):
            break
    location = input("请输入电话归属地：")
    # 生成号码
    allnum = completion(str(head)[:3], str(tail))
    # 跨线程读取数据
    q = multiprocessing.Queue()
    # 存储所有结果
    result = []
    for i in range(10):  # 开启5个子进程执行fun1函数
        arglist = allnum[(i) * (len(allnum)) // 10:(i + 1) * len(allnum) // 10]
        p = Process(target=judlocation, args=(arglist, location, q))  # 实例化进程对象
        p.start()
        result = result + (q.get())
        p.join()

    print(len(result))
    outfile(result)


if __name__ == '__main__':
    createnum()
