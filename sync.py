#!/usr/bin/env python3
import sys
import os
import csv
from operator import itemgetter

# 这个文件用来同步Firmnet上Send和Receive的偏移地址
# 在Firmnet上，Send类型点的偏移地址，是手工指定的，
# 而Receive类型点的偏移地址，是从Send继承来的
# 手工继承（填写）的话太麻烦，还容易错，所以写了个脚本实现。


def file_validation(csv_list):
    # 在正式处理csv文件之前，进行一系列校验
    # 校验1： 如果文件夹中没有任何文件，则直接退出
    if len(csv_list) == 0:
        input('在sync文件夹中没有待处理的文件，按任意键退出。。。')
        sys.exit(1)

    # 如果有文件，检查文件名中是否有download或者netdev字符串
    result = []
    for csv_file in csv_list:
        if 'download' in csv_file.lower():
            result.append('has_download')
        if 'netdev' in csv_file.lower():
            result.append('has_netdev')

    # 如果文件中不存在环网点表，只对datalink的recv进行同步
    if not 'has_download' in result:
        print('文件夹中没有环网文件download，无法同步环网类的recv信号偏移地址，只对datalink点进行同步，请知晓。')
    # 如果文件中不存在netdev类型点表，相当于不存在
    if not 'has_netdev' in result:
        input('文件夹中没有netdev类的通信清单，程序不再执行，请按任意键退出。。。')
        sys.exit(1)


def abs_path(filelist):
    # 为filelist中所有文件生成绝对路径文件名
    abspath_filelist = []
    for f in filelist:
        f_abspath = os.path.join(os.getcwd(), 'sync', f)
        abspath_filelist.append(f_abspath)

    return abs_path_filelist


def collect_send(filelist):
    # 分别返回datalink和firmnet的所有send信号
    # 两个list
    datalink_send_list = []
    firmnet_send_list = []

    for f in filelist:
        if 'netdev' in f:
            # 收集datalink的send信号（整行保存）
            csv_reader = csv.read(f, 'r', encoding='gbk')
            next(reader) # 甩掉首行
            for row in list(csv_reader):
                if row[] # TODO 用第几列进行判断？

        elif 'download' in f:
            # 收集firmnet的send信号（整行保存）

    return datalink_send_list, firmnet_send_list

def sync_offset(csvfile):
    # with open(csvfile, 'r', encoding='gbk') as in_file, \
    #      open(newfile, 'w', encoding='gbk') as out_file:
    pass
        



def main():
    # TODO 基本思路
    # 用户把需要填写的csv（target），和已经填写好Send偏移地址的csv文件（source）放在同一文件夹内
    # 先open所有上述文件
    # 在需要填写offset的文件中，遍历所有行
    # 如果这一行是环网点、且点类型是Receive，那么:
    #   - 根据点名，在source中找对应点名，且校验找到的点是否为Send类型
    #   - 如果找到的点满足上条要求，则把source中的offset写入到target的相应位置上

    if not os.path.isdir('sync'):
        os.mkdir('sync')

    csvfiles = os.listdir('./sync')
    file_validation(csvfiles)

    # 生成所有绝对路径csv文件的list
    # 同时生成一个所有send信号的数据体（TODO 什么数据类型？）
    csvfiles_abspath = abs_path(csvfiles)  # return a list
    send_signals_pool = collect_send(csvfiles_abspath) # return a list of lists

    for csvfile in csvfiles:
        # 如果文件是csv格式，而且文件名前4位不是sync开头，则对该文件进行处理
        if csvfile[-3: ].lower() == 'csv' and csvfile[ :4].lower() != 'sync':
            # 生成
            in_file_path = os.path.join(os.getcwd(), 'offset', csvfile)
            out_file_path = os.path.join(os.getcwd(), 'offset', 'offset_' + csvfile)
            csv_handler(in_file_path, out_file_path)
            print(os.path.basename(csvfile) + ' 处理完毕')
    input('按任意键退出...')
        sync_offset(csvfile)


if __name__ == '__main__':
    main()
