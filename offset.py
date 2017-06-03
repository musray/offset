#!/usr/bin/env python3
import os
import csv
import sys


def datalink_offset_calc(allocator, signal_type):
    # allocator: 累加的偏移地址
    # signal_type: csv第2列（0起）的值。

    bool_signal_length = 2
    device_signal_length = 2
    real_signal_length = 8

    if signal_type == 'bool_signal':
        allocator += bool_signal_length
    elif signal_type == 'device_signal':
        allocator += device_signal_length
    elif signal_type == 'real_signal':
        allocator += real_signal_length

    return allocator


def firmnet_offset_calc(allocator):
    # 增加规则
    return allocator


def csv_handler(in_file_path, out_file_path):
    # file_name = os.listdir('./sheets')[2]
    # file_path = os.path.join(os.getcwd(), 'sheets', file_name)
    # new_file_path = os.path.join(os.getcwd(), 'sheets', 'new_' + file_name)

    with open(in_file_path, 'r', encoding='gbk') as csv_in, \
         open(out_file_path, 'w', encoding='gbk', newline='') as csv_out:

        reader = csv.reader(csv_in, delimiter=',')
        writer = csv.writer(csv_out, delimiter=',')

        # 先写header，增加title
        header = next(reader)
        header[-1] = '偏移'
        writer.writerow(header)

        # 定义该站的各个站点
        datalink_allocator = 0
        firmnet_allocator = 0

        # 计算每一行的偏移地址
        for row in reader:
            if row[10]:
                # row[10]有内容，说明这一行是环网
                # firmnet有哪些具体规则？
                pass
            else:
                # row[10]没内容，说明这一行是datalink
                # datalink有哪些具体规则？
                datalink_allocator = datalink_offset_calc(datalink_allocator, row[2])
                row[-1] = datalink_allocator
                writer.writerow(row)


def main():
    # 如果当前文件夹内不存在offset文件夹
    # 则新建文件夹
    if not os.path.isdir('offset'):
        os.mkdir('offset')

    # 遍历给定文件夹内的所有文件
    # 如果是csv文件，则：
    #   - 挨个处理
    csvfiles = os.listdir('./offset')

    if len(csvfiles) == 0:
        input('在offset文件夹中没有待处理的文件，按任意键退出。')
        sys.exit(1)

    for csvfile in csvfiles:
        if csvfile[-3: ].lower() == 'csv' and csvfile[ :6].lower() != 'offset':
            # print('\nDEBUG')
            # print(csvfile)
            in_file_path = os.path.join(os.getcwd(), 'offset', csvfile)
            out_file_path = os.path.join(os.getcwd(), 'offset', 'offset_' + csvfile)
            csv_handler(in_file_path, out_file_path)
            print(os.path.basename(csvfile) + ' 处理完毕')
    input('按任意键退出...')

if __name__ == '__main__':
    main()
