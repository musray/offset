#!/usr/bin/env python3
import sys
import os
import csv
from operator import itemgetter

# ---------------------------------------------- #
#                 Abstraction
# 这个文件用来同步Firmnet上Send和Receive的偏移地址
# 在Firmnet上，Send类型点的偏移地址，是手工指定的，
# 而Receive类型点的偏移地址，是从Send继承来的
# 手工填写的话太麻烦，还容易错，所以写了个脚本实现。
# ---------------------------------------------- #



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


def get_offset_value(name, ring, data):
    # 此函数只在sync_offset中被调用，其中：
    #   - name: string，信号名
    #   - ring: int, 环网号，1，2，3，4
    #   - data: 三维数组，环网数据

    #
    # DEBUG
    #
    # print(name, ring)

    warning_info = ['Safety System BUS(offset_download_1.csv)', 'Safety BUS Train A(offset_download_2.csv)', \
                    'Safety BUS Train B(offset_download_3.csv)', 'HM Data BUS(offset_download_4.csv)']

    # 下面这个list comprehension的意图：找到 name 所在的行
    # 1. 遍历data中第ring-1个元素所对应的二维数组，找到 name 所在的环网的数据
    # 2. 如果row[2]点名 == name，并且row[1]的内容为send或者dss，
    # 3. 把这个row返回。（根据点表的填写规则，只能有唯一的row被返回）
    target_row = [row for row in data[ring-1] if row[2].lower() == name.lower() and
                  (row[1].lower() == 'send' or row[1].lower() == 'dss')]

    # 做一个校验，如果返回的target_row为空，说明相应的环网csv文件不在 sync 文件夹里（产生这种情况的最可能原因）
    if not target_row:
        input('错误。请检查 sync 中是否包含 %s 的相应文件。\n按任意键退出...' % warning_info[ring - 1])
        sys.exit(1)

    # 把offset值强制成int返回
    return int(target_row[0][6].strip())


def sync_offset(netdev_file, firmnet_data):
    path, basename = os.path.split(netdev_file)
    new_file = os.path.join(path, 'sync_' + basename)
    with open(netdev_file, 'r', encoding='gbk') as in_file, \
         open(new_file, 'w', encoding='gbk', newline='') as out_file:

        # 把csv的内容读出来
        netdev_list = list(csv.reader(in_file))

        # 把需要新建的文件，用csv writer打开
        writer = csv.writer(out_file)

        # 遍历所有行，如果：
        # 1. row[10]中有"环点"字样，则说明该行是环网的点，看倒数第二位的环号，赋值给变量（校验环网的csv是不是在sync文件夹中）
        # 2. row[5]中的设备类型如果是send，则：用row[1]的点名去firmnet_data里找相应的点，偏移地址写到netdev_list的row[11]中
        for row in netdev_list:
            # 是环网上的点？
            if '环点' in row[10]:
                net_ring = int(row[10].strip()[-2])
                signal_name = row[1]
                # 调用get_offset_value
                offset_value = get_offset_value(signal_name, net_ring, firmnet_data)  # 返回值是int
                row[11] = offset_value

        # 把需要新建的文件，用csv writer打开
        writer = csv.writer(out_file)
        writer.writerows(netdev_list)


def get_firmnet_data(firmnet_files):
    # 把firmnet文件挨个打开，存到一个三维list中
    # 问题：如果只有三维list，如何确保firmnet1, 2, 3, 4的数据在三维数组中的排列顺序？（答案：在代码里找）
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
            # sequence决定了data在firmnet_data这个三维list中的顺序
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
    # 1. [DONE]用户把带有offset的NETDEV和download，都放到sync中
    # 2. [DONE]打开所有的download文件，把所有行都读出来，每一个文件存到一个list中
    # 3. 遍历所有的netdev.csv：
    #   - 找到环网的点
    #   - 对于环网上四个类型的点，dss/dsr/send/recv，都按照点名和环网号，去对应的环网csv中去找send或dss的点

    #
    # 第1步
    # 检查是否有 sync 文件夹
    #
    if not os.path.isdir('sync'):
        # 没有的话新建一个，并退出
        os.mkdir('sync')
        input('当前路径下没有 sync 文件夹，已经为你新建。')
        sys.exit(1)

    #
    # 第2步
    # 遍历 sync 内的所有文件，分别找到offset_netdev和offset_download
    # ，两个files中已经是 [ !绝对路径! ]
    #
    netdev_files, firmnet_files = file_validation(os.listdir('./sync'))

    #
    # 第3步
    # 生成一个存有firmnet.csv数据的三维数组
    # 数组中从0到3分别为Safety System BUS, Safety BUS TrainA, Safety_BUS TrainB 和 HM Data BUS
    #
    firmnet_data = get_firmnet_data(firmnet_files)

    #
    # 第4步
    # 在netdev.csv中，逐个填写
    # 找到其中环网的点，从firmnet_data中找到其对应的点名，拷贝offset值并粘贴
    #
    for netdev_file in netdev_files:
        # 先cue一下焦急等待的群众：
        print('%s 处理中，请稍候...' % netdev_file)
        sync_offset(netdev_file, firmnet_data)
        print('已完成！')

    # Test and DEBUG
    # ttest_get_firmnet_data(firmnet_data)
    input('%d 个文件已成功添加偏移地址。\n按任意键退出...' % len(netdev_files))

if __name__ == '__main__':
    main()
