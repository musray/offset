#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import csv
import re
import pprint
import node_ring_relation
pp = pprint.PrettyPrinter(indent=4)

# ------------------------------------------------------- #
#                 Abstraction
# 实现路径：
# 1. 把firmnet.csv和netdev.csv逐个读一遍，所有send点，放到一个datapool(list)里
# 2. 对每一个netdev.csv:
#   - 读文件
#   - 找Receive
#   - 去datapool里找这个Receive对应的send点
#   - 把send的offset，写到Receive里
#   - 生成sync_netdev.csv，包含所有send，receive的offset
# ------------------------------------------------------- #


# 有datalink和环网通信的站
# list中的数字是站号，人工确定
DATALINK_FIRMNET_SEQ = ['1', '2', '3', '4', '5', '6', '7', '8', '11', '12', '17',
                        '18', '19', '41', '42', '47', '48', '49']

# 只有环网通信的站
# 一个项目的最大站号是63
FIRMNET_SEQ = [str(x) for x in range(1, 64) if str(x) not in DATALINK_FIRMNET_SEQ]

# NET_NODE_RELATION = {
#     '0': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '21', '18', '19', '23', '24', '33', '48', '49', '63'],
#     '1': ['11', '12', '13', '14', '15', '16', '17', '18', '19', '25', '26', '27', '28', '29', '30', '31', '32'],
#     '2': ['41', '42', '43', '44', '45', '47', '48', '49', '55', '56', '57', '58', '59', '60', '61', '62'],
#     '3': ['10', '22', '25', '27', '28', '29', '30', '31', '55', '57', '58', '59', '61', '60']
# }

#
#
# NODE_RING_RELATION = {
#     '1': ['1'],
#     '2': ['1'],
#     '3': ['1'],
#     ......
#     '63': ['3', '4']
#
NODE_RING_RELATION = node_ring_relation.NODE_RING_RELATION


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


def query_firmnet(name, order, collection, rings):
    '''
    :param name: string, 信号名 
    :param order: string, 站号
    :param collection: 二维数组，环网数据
    :param ring: string，环号
    :return offset_value: string, offset值
    '''

    # 下面这个list comprehension的意图：找到 name 所在的行
    # 1. 遍历data中第ring-1个元素所对应的二维数组，找到 name 所在的环网的数据
    # 2. 如果row[2]点名 == name，并且row[1]的内容为send或者dss，
    # 3. 把这个row返回。（根据点表的填写规则，只能有唯一的row被返回）
    # target_row = [row for row in collection[order-1] if row[2].lower() == name.lower() and
    #               (row[1].lower() == 'send' or row[1].lower() == 'dss')]


    # 针对DTC等有datalink，和两个环网的情况，增加了if not ring的条件判断
    # 如果ring已经是1，2，3，4的某一个值，那让select_net直接等于ring
    # 否则，使用order在NET_NODE_RELATION里找对应的ring
    offset_value = False
    if rings:
        # select_net = str(int(ring) - 1) # 清单里的环网从1开始，但firmnent_data里是从0开始
        # rings是一个清单代表的实际控制站可能在的环网号
        # ring是其中一个环网号
        for ring in rings:
            for row in collection[int(ring) - 1]:
                if name.lower() == row[2].lower():
                    # 如果便宜地址所在列有内容，说明当前点确实在目前查询的环网内
                    if row[6]:
                        offset_value = row[6]
                        break
    else:
        # for net, nodes in NET_NODE_RELATION.items():
        #     if order in nodes:
        #         select_net = net
        print('获得环网数据失败，退出。。。')
        sys.exit(1)

    # if not right_net:
    #     pass # TODO 此处需要处理异常：netdev_n中的n有问题

    #
    # DEBUG
    #
    # print('select net is %s' % select_net)
    # print('collection[%s] is ' % select_net)
    # pp.pprint(collection[int(select_net)])

    # offset_value = False
    # for row in collection[int(select_net)]:
    #     if name.lower() == row[2].lower():
    #         offset_value = row[6] # offset_download的第6列

    # if not offset_value:
    #     pass # TODO 此处需要处理异常：collection中没有找到name

    # print('offset value is %s' % offset_value)
    return offset_value


def query_datalink(name, order, collection):
    '''
    :param name: string, 信号名 
    :param order: string, 站号
    :param collection: 三维数组，环网数据
    :return offset_value: string, offset值
    '''
    offset_value = False

    for row in collection:
        if name.lower() == row[1].lower():
            offset_value = row[11]

    if not offset_value:
        # DEBUG
        print('%s 没找到' % name)

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
                sequence = re.findall(r'\d+', firmnet_file)[0]
                if not sequence in ['1', '2', '3', '4']:
                    input('%s 文件命名错误，文件名最后一位必须是1-4的数字。请检查文件名后重新运行程序。\n按任意键退出...')

            except ValueError:
                input('%s 文件命名错误，确认后重新运行程序。\n按任意键退出...')
                sys.exit(1)

            # sequence决定了data在firmnet_data这个三维list中的顺序
            # 从data里筛选出send和dss类型的点，写入到firmnet_data指定的sublist里
            firmnet_data[int(sequence) - 1] = [row for row in data if row[1].lower()=='send' or row[1].lower()=='dss']

    # DEBUG
    # print('firmnet data is')
    # pp.pprint(firmnet_data)

    return firmnet_data


def get_datalink_data(netdev_files):
    # 把固定几个netdev文件（RPC，ESF和DTC的几个文件）挨个打开，
    # 把所有的send点，存到一个大list中
    # 新建一个list，用来保存所有netdev文件里datalink的内容
    datalink_data = []
    for netdev_file in netdev_files:
        # 用re提取文件名中的数字
        sequence = re.findall(r'\d+', netdev_file)[0]
        # 如果数字在DATALINK_FIRMNET_SEQ中能找到
        # 说明是一个既有环网，又有datalink的清单
        if sequence in DATALINK_FIRMNET_SEQ:
            with open(netdev_file, 'r', encoding='gbk') as n_f:
                data = list(csv.reader(n_f))
                # 找出没有'环网'字样，而且是send类型的点
                datalink_data.extend([row for row in data if row[5].lower()=='send' and '环' not in row[10]])

    # print(len(datalink_data))

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
        #   - SCID的表，没有"环点"的说明，所以要找两遍（自己所在的SA/SB找一遍，HM找一遍）
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
        order = re.findall(r'\d+', basename)[0]
        offset_value = 'not found'

        # 如果文件中只有环网的点：
        if order in FIRMNET_SEQ:
            rings = NODE_RING_RELATION[order]
            for row in netdev_list:
                # if row[5].lower() == 'recv':
                # 正式获得offset的值
                # offset_value可能的值是False或者一个'0'， '1'， '2'。。。的字符串
                offset_value = query_firmnet(row[1], order, firmnet_data, rings)

                if offset_value:
                    row[11] = offset_value
                    # print('row[11] is %s' % row[11])
            # 把相关内容写入到csv.writer中去
            writer.writerows(netdev_list)

        #
        # new thought
        #
        # 如果文件中既有环网的点，也有datalink的点：
        # 看row[10]:
        # 有环点，查环网；是哪个环，查哪个环
        # 没有环点，查datalink

        # 如果文件中既有环网的点，也有datalink的点：
        elif order in DATALINK_FIRMNET_SEQ:
            for row in netdev_list:
                # 如果该行是个环点
                if '环点' in row[10]:
                    # row[1]:点名；order：文件名中的数字；ring：环号；firmnent_data: firmnet的发送数据
                    rings = NODE_RING_RELATION[order]
                    offset_value = query_firmnet(row[1], order, firmnet_data, rings)
                    if offset_value:
                        row[11] = offset_value
                # 如果该行是个datalink点，且它是一个recv或者dsr类型，则处理它
                elif '环点' not in row[10] and row[5].lower() in ['recv', 'dsr']:
                    offset_value = query_datalink(row[1], order , datalink_data)
                    if offset_value:
                        row[11] = offset_value
                    # print(offset_value)

                # offset写入
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
        # CALL
        sync_offset(netdev_file, firmnet_data, datalink_data)
        print('已完成！')

    # Test and DEBUG
    # ttest_get_firmnet_data(firmnet_data)
    input('%d 个文件已成功添加偏移地址。\n按任意键退出...' % len(netdev_files))

if __name__ == '__main__':
    main()
