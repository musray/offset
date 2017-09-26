#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import csv
from operator import itemgetter
import pprint
pp = pprint.PrettyPrinter(indent=4)

# ---------------------------------------------- #
#                 Abstraction
# 实现路径：
# 1. 把firmnet.csv和netdev.csv逐个读一遍，所有send点，放到一个datapool(list)里
# 2. 对每一个netdev.csv:
#   - 读文件
#   - 找Receive
#   - 去datapool里找这个Receive对应的send点
#   - 把send的offset，写到Receive里
#   - 生成sync_netdev.csv，包含所有send，receive的offset
# ---------------------------------------------- #

# TODO 确定哪些netdev.csv中包含datalink
# TODO 1. 确定那些清单中有firmnet和datalink，哪些只有firmnent
FIRMNET_SEQ = [str(x) for x in range(13, 60)] # 返回13到59的一个list
DATALINK_SEQ = [str(x) for x in range(1, 13)] # 返回1 到12的一个list
NET_NODE_RELATION = {
    '0': [str(x) for x in range(1, 9)], # RPC1,2,3,4, 在0号环网SSB
    '1': ['12', '13', '14'],     # TODO 哪些站，在1号环网上
    '2': ['15', '16', '17'],     # TODO 哪些站，在2号环网上
    '3': ['18']                             # TODO 哪些站，在3号环网上
}


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
            # print('catch it %s' % file_abspath)
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


def query_firmnet(name, order, collection):
    '''
    :param name: string, 信号名 
    :param order: string, 站号
    :param collection: 三维数组，环网数据
    :return offset_value: string, offset值
    '''

    # warning_info = ['Safety System BUS(offset_download_1.csv)', 'Safety BUS Train A(offset_download_2.csv)', \
    #                 'Safety BUS Train B(offset_download_3.csv)', 'HM Data BUS(offset_download_4.csv)']

    # 下面这个list comprehension的意图：找到 name 所在的行
    # 1. 遍历data中第ring-1个元素所对应的二维数组，找到 name 所在的环网的数据
    # 2. 如果row[2]点名 == name，并且row[1]的内容为send或者dss，
    # 3. 把这个row返回。（根据点表的填写规则，只能有唯一的row被返回）
    # target_row = [row for row in collection[order-1] if row[2].lower() == name.lower() and
    #               (row[1].lower() == 'send' or row[1].lower() == 'dss')]

    # DEBUG
    # print('order is %s' % order)
    # print('collection is')
    # pp.pprint(collection)

    select_net = False
    for net, nodes in NET_NODE_RELATION.items():
        if order in nodes:
            select_net = net

    # if not right_net:
    #     pass # TODO 此处需要处理异常：netdev_n中的n有问题

    print('select net is %s' % select_net)
    offset_value = False
    for row in collection[int(select_net)]:
        if name.lower() == row[2].lower():
            offset_value = row[6] # offset_download的第6列

    # if not offset_value:
    #     pass # TODO 此处需要处理异常：collection中没有找到name

    return offset_value

def query_datalink(name, order, collection):
    '''
    :param name: string, 信号名 
    :param order: string, 站号
    :param collection: 三维数组，环网数据
    :return offset_value: string, offset值
    '''
    offset_value = False
    return offset_value


def get_firmnet_data(firmnet_files):
    # 把firmnet文件挨个打开，存到一个三维list中
    # 问题：如果只有三维list，如何确保firmnet1, 2, 3, 4的数据在三维数组中的排列顺序？（答案：在代码里找）
    firmnet_data = [[], [], [], []]
    for firmnet_file in firmnet_files:
        with open(firmnet_file, 'r', encoding='gbk') as f_f:
            data = list(csv.reader(f_f))

            # 尝试在文件名的倒数第5位获取数字，分别代表一种firmnet环网：1：SSB；2：SB_A；3：SB_B；4：HM
            try:
                sequence = firmnet_file[-5]
                if not sequence in ['1', '2', '3', '4']:
                    input('%s 文件命名错误，文件名最后一位必须是1-4的数字。请检查文件名后重新运行程序。\n按任意键退出...')

            except ValueError:
                input('%s 文件命名错误，确认后重新运行程序。\n按任意键退出...')
                sys.exit(1)

            # sequence决定了data在firmnet_data这个三维list中的顺序
            # 从data里筛选出send和dss类型的点，写入到firmnet_data指定的sublist里
            firmnet_data[int(sequence) - 1] = [row for row in data if row[1].lower()=='send' or row[1].lower()=='dss']

    # DEBUG
    print('firmnet data is')
    pp.pprint(firmnet_data)

    return firmnet_data


def get_datalink_data(netdev_files):
    # 把固定几个netdev文件（RPC，ESF和DTC的几个文件）挨个打开，
    # 把所有的send点，存到一个大list中
    # 新建一个list，用来保存所有netdev文件里datalink的内容
    datalink_data = []
    for netdev_file in netdev_files:
        # 用文件名的倒数第5位的数字，判断netdev中是否包含datalink
        sequence = netdev_file[-5]
        if sequence in DATALINK_SEQ:
            # print('sequence is %s' % sequence)
            with open(netdev_file, 'r', encoding='gbk') as n_f:
                data = list(csv.reader(n_f))
                # print(data)
                datalink_data.extend([row for row in data if row[5].lower()=='send' and '环' not in row[10]])

    print(len(datalink_data))
    # print(datalink_data)
    return datalink_data


def sync_offset(netdev_file, firmnet_data, datalink_data):
    path, basename = os.path.split(netdev_file)
    new_file = os.path.join(path, 'sync_' + basename)
    with open(netdev_file, 'r', encoding='gbk') as in_file, \
            open(new_file, 'w', encoding='gbk', newline='') as out_file:

        # 把csv的内容读出来
        netdev_list = list(csv.reader(in_file))

        # 把需要新建的文件，用csv writer打开
        writer = csv.writer(out_file)

        # 遍历所有行，并进行一系列判断：
        # 1. netdev_n.csv中，n是12及大于12的值，则这个文件中都是环网的点。
        # 2. netdev_n.csv中，n是1-11之间的值，则这个文件中有环网的点，也有datalink的点
        #
        # TODO 2. 确定只有firmnent的清单中，序号和环网号的对应关系
        # case1 如果都是firmnet的点：
        #   - 遍历所有点，找receive的点
        #   - 判断它是哪个环上的点
        #   - 调用firmnet_data中对应环的数据
        #   - 查到这个点名对应的行，返回offset值
        #   - 填回list中
        #
        # case2 如果是firmnet和datalink都有：
        #   - 遍历所有点，找receive的点
        #   - 如果row[10]有'环点'字样，则去firmnent_data里找这个点，并获取offset值
        #   - 如果row[10]中没有'环点'字样，则去datalink里找这个点，并获取offset值
        #   - 填回list中
        #
        # 1. row[10]中有"环点"字样，则说明该行是环网的点，看倒数第二位的环号，赋值给变量（校验环网的csv是不是在sync文件夹中）
        # 2. row[5]中的设备类型如果是send，则：用row[1]的点名去firmnet_data里找相应的点，偏移地址写到netdev_list的row[11]中

        # 提取netdev_n.csv中的n，作为order
        order = basename[-5]
        # 如果文件中只有环网的点：
        if order in FIRMNET_SEQ:
            for row in netdev_list:
                # if row[5].lower() == 'recv':
                # 正式获得offset的值
                # offset_value可能的值是False或者一个'0'， '1'， '2'。。。的字符串
                offset_value = query_firmnet(row[1], order, firmnet_data)

                if offset_value:
                    row[11] = offset_value
            # 把相关内容写入到csv.writer中去
            writer.writerows(netdev_list)

        elif order in DATALINK_SEQ:
            for row in netdev_list:
                # 如果该行是个环点
                if '环点' in row[10]:
                    offset_value = query_firmnet(row[1], order, firmnet_data)
                    # print('name is %s' % row[1])
                    # print('offset value is %s' % offset_value)
                # 如果该行是个datalink点，且它是一个recv或者dsr类型，则处理它
                elif '环点' not in row[10] and row[5].lower() in ['recv', 'dsr']:
                    offset_value = query_datalink(row[1], order , datalink_data)
                    if offset_value:
                        row[11] = offset_value
            # 把相关内容写入到csv.writer中去
            writer.writerows(netdev_list)

        else:
            # TODO 此处需要处理文件名称不符合规范的异常
            pass


def main():
    # 基本思路
    # 1. 用户把带有offset的NETDEV和download，都放到sync中
    # 2. 遍历所有的download文件，把所有send行都读出来，整体保存到一个新list中（list or generator?）
    # 3. 遍历所有的netdev文件，把所有的send行都读出来，整体保存到一个新list中(list or generator?)
    # 4. 逐个打开netdev文件
    #   - 写入到一个新list
    #   - 找到receive或者dsr类的点
    #   - 判断是 datalink 还是 firmnet
    #   - 到相应的 datapool 中检索
    #   - offset 写到list中

    #
    # 第1步
    # 准备工作：检查是否有 sync 文件夹
    if not os.path.isdir('sync'):
        # 没有的话新建一个，并退出
        os.mkdir('sync')
        input('当前路径下没有 sync 文件夹，已经为你新建。')
        sys.exit(1)

    #
    # 第2步
    # 遍历 sync 内的所有文件，分别找到offset_netdev和offset_download
    # ，注意：以下两个files中已经是 [ !绝对路径! ]
    #
    netdev_files, firmnet_files = file_validation(os.listdir('./sync'))

    #
    # 第3步
    # 生成一个存有firmnet.csv数据的三维数组
    # 数组中从0到3分别为Safety System BUS, Safety BUS TrainA, Safety_BUS TrainB 和 HM Data BUS
    #
    firmnet_data = get_firmnet_data(firmnet_files)
    datalink_data = get_datalink_data(netdev_files)

    #
    # 第4步
    # 逐个打开netdev.csv，保存成一个新的list
    # 找到其中receive的点，判断其所属的网络：
    #   - 如果是datalink的点：从datalink_data中查找其offset值
    #   - 如果是firmnet的点，从firmnet_data中查找其offset的值
    #
    #
    for netdev_file in netdev_files:
        # 先cue一下焦急等待的群众：
        print('%s 处理中，请稍候...' % netdev_file)
        sync_offset(netdev_file, firmnet_data, datalink_data)
        print('已完成！')

    # Test and DEBUG
    # ttest_get_firmnet_data(firmnet_data)
    input('%d 个文件已成功添加偏移地址。\n按任意键退出...' % len(netdev_files))

if __name__ == '__main__':
    main()
