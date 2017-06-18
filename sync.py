#!/usr/bin/env python3
import sys
import os
import csv
from operator import itemgetter

# 这个文件用来同步Firmnet上Send和Receive的偏移地址
# 在Firmnet上，Send类型点的偏移地址，是手工指定的，
# 而Receive类型点的偏移地址，是从Send继承来的
# 手工填写的话太麻烦，还容易错，所以写了个脚本实现。


def file_validation(csv_list):
    # csv_list 是 sync 文件夹内所有文件的清单
    # ，我们要把firmnet和netdev两种文件找出来，分别放入各自的list
    # ，并将其return(return的是绝对路径)

    firmnet_list = []
    netdev_list = []

    #
    # 校验1： 如果文件夹中没有任何文件，则直接退出
    #
    if len(csv_list) == 0:
        input('在sync文件夹中没有待处理的文件，按任意键退出。。。')
        sys.exit(1)

    #
    # 校验2：文件夹中必须同时有netdev何download文件
    # 按关键字，把csv文件分为firmnet和netdev两类
    #
    for csv_file in csv_list:
        if 'offset_download' in csv_file.lower()[0:15]:
            # 生成绝对路径，append到list中
            file_abspath = os.path.join(os.getcwd(), 'sync', csv_file)
            firmnet_list.append(file_abspath)
        elif 'offset_netdev' in csv_file.lower()[0:13]:
            # 生成绝对路径，append到list中
            file_abspath = os.path.join(os.getcwd(), 'sync', csv_file)
            print('catch it %s' % file_abspath)
            netdev_list.append(file_abspath)

    #
    # 校验3：firmnet和netdev文件必须同时存在
    # 原因：所谓同步功能，实际上就是把firmnet表里生成的send和dss类偏移地址，相应拷贝到netdev里去
    # ，所以两者必须都存在，才有继续执行的意义。
    #
    if len(firmnet_list) == 0:
        input('sync 文件夹中没有环网文件sync_download.csv，无法执行环网偏移地址同步。\n按任意键退出...')
        sys.exit(1)
    # 如果文件中不存在netdev类型点表，相当于不存在
    if len(netdev_list) == 0:
        input('文件夹中没有netdev类的通信清单，无法执行环网偏移地址同步。\n按任意键退出...')
        sys.exit(1)

    return netdev_list, firmnet_list


# def collect_send(filelist):
#     # 分别返回datalink和firmnet的所有send信号
#     # 两个list
#     datalink_send_list = []
#     firmnet_send_list = []
#
#     for f in filelist:
#         if 'netdev' in f:
#             # 收集datalink的send信号（整行保存）
#             csv_reader = csv.read(f, 'r', encoding='gbk')
#             next(reader) # 甩掉首行
#             for row in list(csv_reader):
#                 if row[] # TODO 用第几列进行判断？
#
#         elif 'download' in f:
#             # 收集firmnet的send信号（整行保存）
#
#     return datalink_send_list, firmnet_send_list


def sync_offset(csvfile):
    # with open(csvfile, 'r', encoding='gbk') as in_file, \
    #      open(newfile, 'w', encoding='gbk') as out_file:
    pass


def get_firmnet_data(firmnet_files):
    # 把firmnet文件挨个打开，存到一个二维list中
    # 问题：如果只有二维list，如何确保firmnet1, 2, 3, 4的数据在二维数组中的排列顺序？
    # 如果不用二维数组，用dict，也许能比较好的解决这个问题
    firmnet_data = [[], [], [], []]
    for firmnet_file in firmnet_files:
        with open(firmnet_file, 'r', encoding='gbk') as f_f:
            data = list(csv.reader(f_f))

            # 尝试在文件名的倒数第5位获取数字，分别代表一种firmnet环网：1：SSB；2：SB_A；3：SB_B；4：HM
            try:
                sequence = int(firmnet_file[-5])
                if not sequence in [1, 2, 3, 4]:
                    input('%s 文件命名错误，文件名最后一位必须是1-4的数字。请检查文件名后重新运行程序。\n按任意键退出...')

            except ValueError:
                input('%s 文件命名错误，确认后重新运行程序。\n按任意键退出...')
                sys.exit(1)
            # sequence决定了data在firmnet_data这个二维list中的顺序
            firmnet_data[sequence - 1] = data

    return firmnet_data


def ttest_get_firmnet_data(data):
    print('+-----------------+')
    print('测试内容：')
    source = '24852'
    target = data[0][8945][6]
    print('\t希望值是 %s，实际得到 %s' % (source, target))
    print('测试结果：')
    if target == source:
        print('\t测试通过！')
    else:
        print('\t测试失败')
    print('+-----------------+')


def main():
    # 基本思路
    # 1. 用户把带有offset的NETDEV和download，都放到sync中
    # 2. 打开所有的download文件，把所有行都读出来，每一个文件存到一个list中
    # 3. 遍历所有的netdev.csv：
    #   - 找到环网的点
    #   - 如果是send/dss，看属于哪个环网，根据点名去对应环网的数据中查offset，写到最后一列
    #   - 如果是recv/dsr，TODO
    # TODO 确认：四个环网上会不会有重名的点？（暂时按没有重名点开发）

    # 检查是否有 sync 文件夹
    if not os.path.isdir('sync'):
        # 没有的话新建一个，并退出
        os.mkdir('sync')
        input('当前路径下没有 sync 文件夹，已经为你新建。')
        sys.exit(1)

    # 遍历 sync 内的所有文件，分别找到offset_netdev和offset_download
    # ，而且都是绝对路径
    netdev_files, firmnet_files = file_validation(os.listdir('./sync'))

    # 生成一个存有firmnet.csv的二维数组
    # 数组中从0到3分别为Safety System BUS, Safety BUS TrainA, Safety_BUS TrainB 和 HM Data BUS
    firmnet_data = get_firmnet_data(firmnet_files)

    # Test and DEBUG
    ttest_get_firmnet_data(firmnet_data)

if __name__ == '__main__':
    main()
