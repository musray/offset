#!/usr/bin/env python3
import os
import csv
import sys
from operator import itemgetter


def sort_datalink(csv_reader):
    # csv_reader是一个csv.reader的object

    # 把csv的reader转化成一个list
    csv_list = list(csv_reader)

    # 根据技术部给的文档，"数据类型"的排列是固定顺序的，次序如下：
    data_type = ['real_signal', 'int_signal', 'real', 'bool_signal', 'int', 'bool', 'device_signal']

    for row in csv_list:
        # 如果说明列没有内容，说明是datalink的点
        if not ('环点' in row[10]):
            # 在数据类型清单中，查该row数据类型对应的index，增加到row的最后
            row.extend([data_type.index(row[2])])
        # 如果说明列有内容，说明是环网点
        else:
            # 将100添加到row的最后。（实际这个地方填什么值都行）
            row.extend([100])

    # 经过以上的处理，csv的数据从11列变成了12列(12列就是辅助列)
    # 根据6, 7, 8, 9, 12列的优先顺序，进行排序，并返回
    sorted_csv_list = sorted(csv_list, key=itemgetter(6, 7, 8, 9, 12))

    # 最后把辅助列删掉
    for row in sorted_csv_list:
        row.pop()

    return sorted_csv_list


def sort_firmnet(csv_reader):
    csv_list = list(csv_reader)

    # 由于firmnet中的偏移地址，有些是int，有些是str（这是一个坑）
    # 所以这里先把offset1中的值全都变成int，再执行排序，否则排序结果是乱的
    for row in csv_list:
        row[6] = int(row[6])

    # firmnet点表的排序规则：
    # 1. 按node排序（表格第0列），保证相同节点的放在一起
    # 2. 按offset1（表格第6列）排序，升序
    # 3. 排序之后，在同一node内，send和dss就按照offset值的升序排列了
    sorted_csv_list = sorted(csv_list, key=itemgetter(0, 6))
    return sorted_csv_list


def datalink_offset_calc(data_list):
    # offset计算规则
    # 1. csv_list已经是按要求排序过了的
    # 2. 以"网口"为单位，内进行offset计算
    # 4. 每个网口的第一个信号，起始地址都是0
    # 5. 第n+1个信号，其offset是offset(n) + DATA_LENGTH
    # 6. DATA_LENGTH长度是固定的，见下面的具体定义

    # 定义数据类型的长度
    data_length = {
        'real_signal': 8,
        'real': 4,
        'int_signal': 4,
        'bool_signal': 2,
        'int': 2,
        'bool': 1,
        'device_signal': 4
    }


    # 定义一个对网口的记录
    port_list = []
    # 起始offset
    start_value = 0
    # offset增量（取决于上一行的数据类型）
    increment = 0

    for row in data_list:

        # 如果该行是datalink：
        if not ('环点' in row[10]):
            # 生成一个全"站"唯一的网口号：机柜号+机笼号+槽号+端口号
            port = str(row[6]) + str(row[7]) + str(row[8]) + str(row[9])
            # 如果改行的网口号，不是第一次出现：
            if port in port_list:
                start_value += increment
                row[11] = start_value
                increment = data_length[row[2]]
            # 如果改行网口号是第一次出现：
            else:
                # 有必要再赋值一遍，因为在进入下一个网口的时候，这个值需要从0开始
                start_value = 0
                # 记录下increment，给下一行用
                increment = data_length[row[2]]
                # 记录下这个端口号
                port_list.append(port)
                # 一个端口的第一个数据点，offset值从0开始
                row[11] = 0

    return data_list


def firmnet_offset_calc(data_list):

    # firmnet offset的计算规则
    # 1. 如果row[1]不是send或dss类型，该行不做处理
    # 2. 如果row[1]是send或dss类型，则：
    #    - 如果站号(node)是第一次遇到，则: 记录row[6]的值，作为decrement_value; row[6] = 0
    #    - 如果站号(node)不是第一次遇到，则：row[6] -= decrement_value

    # 新建一个站号node列表
    node_list = []

    # 生成一个用于修正偏移地址的递减值
    # 在正式的数据处理中，每一个node的现有最小偏移地址，会赋给decrement
    decrement = 0

    for row in data_list:
        # 如果 direction 列的内容是 send 或 dss（dss是device signal的send信号）
        if row[1].lower() == 'send' or row[1].lower() == 'dss':
            # 该节点的第2行至最后一行
            if row[0] in node_list:
                row[6] = int(row[6]) - decrement
            # 该节点的第1行
            else:
                node_list.append(row[0])  # row[0]是node号
                decrement = int(row[6])   # row[6]是原offset
                row[6] = 0                # 将该行offset设为0

    return data_list


def csv_handler(in_file_path, out_file_path):
    # file_name = os.listdir('./sheets')[2]
    # file_path = os.path.join(os.getcwd(), 'sheets', file_name)
    # new_file_path = os.path.join(os.getcwd(), 'sheets', 'new_' + file_name)

    with open(in_file_path, 'r', encoding='gbk') as csv_in, \
         open(out_file_path, 'w', encoding='gbk', newline='') as csv_out:

        reader = csv.reader(csv_in, delimiter=',')
        writer = csv.writer(csv_out, delimiter=',')

        # 如果文件是datalink清单
        if 'netdev' in in_file_path.lower():

            # 先写header，增加title
            header = next(reader)
            header[-1] = '偏移'
            writer.writerow(header)

            # 生成一个排序后的csv数据list
            sorted_csv_list = sort_datalink(reader)
            # 为datalink类型数据生成offset
            list_with_offset = datalink_offset_calc(sorted_csv_list)

        # 如果文件是firmnet清单
        elif 'download' in in_file_path.lower():

            # header不需要处理，直接写到writer里去
            header = next(reader)
            writer.writerow(header)

            # 根据Firmnet的排序要求，对数据进行排序
            sorted_csv_list = sort_firmnet(reader)
            # 为firmnet类型数据生成offset
            list_with_offset = firmnet_offset_calc(sorted_csv_list)

        # 将生成的最终数据写入目标文件
        writer.writerows(list_with_offset)


def main():
    # 如果当前文件夹内不存在offset文件夹
    # 则新建文件夹
    if not os.path.isdir('offset'):
        input('没有发现 offset 文件夹，已为你新建。\n请将csv文件放入其中，再运行本程序。\n按任意键退出...')
        os.mkdir('offset')
        sys.exit(1)

    # 遍历给定文件夹内的所有文件
    # 如果是csv文件，则：
    #   - 挨个处理
    csvfiles = [item for item in os.listdir('./offset') if '.csv' == item[-4:].lower()]

    # 在offset文件夹中没有csv文件
    if len(csvfiles) == 0:
        input('在offset文件夹中没有待处理的文件，按任意键退出...')
        sys.exit(1)

    hasTarget = False
    for csvfile in csvfiles:
        if csvfile[:6].lower() == 'netdev' or csvfile[:8].lower() == 'download':
            hasTarget = True
            # print('\nDEBUG')
            # print(csvfile)
            in_file_path = os.path.join(os.getcwd(), 'offset', csvfile)
            out_file_path = os.path.join(os.getcwd(), 'offset', 'offset_' + csvfile)

            # 调用csv_handler
            csv_handler(in_file_path, out_file_path)

            # 每一个文件处理万之后，hint一下用户
            print(os.path.basename(csvfile) + ' 处理完毕')

    # 如果没有名称中带有 netdev 或者 download 的文件，要hint一下
    if hasTarget:
        input('按任意键退出...')
    else:
        input('在 offset 文件夹中没有 DEVNET 或 DOWNLOAD 类的 csv 文件。按任意键退出...')

if __name__ == '__main__':
    main()
