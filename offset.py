#!/usr/bin/env python3
import os
import csv
import sys
from operator import itemgetter


def sort_datalink(csv_reader):
    # csv_reader��һ��csv.reader��object

    # ��csv��readerת����һ��list
    csv_list = list(csv_reader)

    # ���ݼ����������ĵ���"��������"�������ǹ̶�˳��ģ��������£�
    data_type = ['real_signal', 'int_signal', 'real', 'bool_signal', 'int', 'bool', 'device_signal']

    for row in csv_list:
        # ��ԭ��:���˵�����е����ݴ���"����"��˵���ǻ����ĵ㣻����Ϊdatalink�ĵ�

        # row[10]�в����������㡯����
        if not ('����' in row[10]):
            # �����������嵥�У����row�������Ͷ�Ӧ��index�����ӵ�row�����
            row.extend([data_type.index(row[2])])

        # ���˵�����С����㡯������˵���ǻ�����
        else:
            # ��100��ӵ�row����󡣣�ʵ������ط���ʲôֵ���У�
            row.extend([100])

    # �������ϵĴ���csv�����ݴ�11��(�հ���)�����12��(12�о��Ǹ�����)
    # ����6, 7, 8, 9, 12�е�����˳�򣬽������򣬲�����
    sorted_csv_list = sorted(csv_list, key=itemgetter(6, 7, 8, 9, 12, 1))

    # ���Ѹ�����ɾ��
    for row in sorted_csv_list:
        row.pop()

    return sorted_csv_list


def sort_firmnet(csv_reader):
    csv_list = list(csv_reader)

    # ����firmnet�е�ƫ�Ƶ�ַ����Щ��int����Щ��str������һ���ӣ�
    # ���������Ȱ�offset1�е�ֵȫ�����int����ִ�����򣬷������������ҵ�
    for row in csv_list:
        row[6] = int(row[6])

    # firmnet�����������
    # 1. ��node���򣨱���0�У�����֤��ͬ�ڵ�ķ���һ��
    # 2. ��offset1������6�У���������
    # 3. ����֮����ͬһnode�ڣ�send��dss�Ͱ���offsetֵ������������
    sorted_csv_list = sorted(csv_list, key=itemgetter(0, 6))
    return sorted_csv_list

def datalink_offset_gen(start, increment, data_lenght):
    '''
    :param start:  ��һ��ͨ�ŵ��ƫ�Ƶ�ַ
    :param increment: ��һ��ͨ�ŵ���������ͳ���
    :param type: ��ͨ�ŵ�����������뱻�������Ĺ�ϵ
    :return: int, ��ͨ�ŵ��ƫ�Ƶ�ַ
    '''

    #
    # �����Ե��offset���б�n����������
    # ֱ�Ӱ�����Ĵ���uncommnet
    #
    # �Ȳ����Ǳ�4���������⣬���һ��������ƫ�Ƶ�ַ
    # base_value = start + increment
    # ���base_value���ڵ�ǰͨ�ŵ���������ͳ���
    # if base_value > data_lenght:
        # ���base_value���ܱ�type����
        # while base_value % data_lenght != 0:
        #     base_value += 1
    # ���base_valueС��type
    # elif base_value <= data_lenght:
        # base_value��1��ֱ�������typeΪֹ
        # while base_value != data_lenght:
        #     base_value += 1

    return start + increment


def datalink_offset_calc(data_list):
    # offset�������
    # 1. csv_list�Ѿ��ǰ�Ҫ��������˵�
    # 2. ��"����"Ϊ��λ���ڽ���offset����
    # 4. ÿ�����ڵĵ�һ���źţ���ʼ��ַ����0
    # 5. ��n+1���źţ���offset��offset(n) + DATA_LENGTH
    # 6. DATA_LENGTH�����ǹ̶��ģ�������ľ��嶨��

    # �����������͵ĳ���
    data_length = {
        'real_signal': [8, 4],
        'real': [4, 4],
        'int_signal': [4, 4],
        'bool_signal': [2, 2],
        'int': [2, 2],
        'bool': [1, 1],
        'device_signal': [4, 4]
    }


    # ����һ�������ڵļ�¼
    port_list = []

    # offset��ʼֵ
    start_value = 0

    # offset��������ʼ��Ϊ0����ʵ��ֵȡ������һ�е��������ͣ�
    increment = 0

    for row in data_list:
        # ���������datalink
        if not ('����' in row[10]):
            # , ������SEND���͵ĵ�
            if 'SEND' in row[5]:
                # ������ݳ���
                # print(increment)
                # ����һ��ȫ"վ"Ψһ�����ںţ������+������+�ۺ�+�˿ں�
                port = str(row[6]) + str(row[7]) + str(row[8]) + str(row[9])

                # ������е����ںţ����ǵ�һ�γ��֣�
                if port in port_list:
                    row[11] = datalink_offset_gen(start_value, increment, data_length[row[2]][1])
                    # ��ǰ���offset������Ϊstart_value����һ��ʹ��
                    start_value = row[11]
                    # ����ͨ�ŵ�����ݳ��ȣ���Ϊ��һ�ֵ�increment
                    increment = data_length[row[2]][0]
                # ����������ں��ǵ�һ�γ��֣�
                else:
                    # �б�Ҫ��start_value��ʼ��һ��
                    # ��Ϊ�ڽ���һ�������ڵ�ʱ�����ֵ��Ҫ��0��ʼ
                    start_value = 0
                    # ��¼������˿ں�
                    port_list.append(port)
                    # һ���˿ڵĵ�һ�����ݵ㣬offsetֵ��0��ʼ
                    row[11] = start_value
                    increment = data_length[row[2]][0]

    return data_list


def offset_gen(base_value, data_lenght):
    '''
    :param base_value: 
    :param data_lenght: 
    :return: 
    '''

    # ���base_value���ڵ�ǰͨ�ŵ���������ͳ���
    if base_value > data_lenght:
        # ���base_value���ܱ�data_length����
        while base_value % data_lenght != 0:
            base_value += 1
    # ���base_valueС��type
    elif base_value <= data_lenght:
        # base_value��1��ֱ�������typeΪֹ
        while base_value != data_lenght:
            base_value += 1

    return base_value

def firmnet_offset_calc(data_list):

    # firmnet offset�ļ������
    # 1. ���row[1]����send��dss���ͣ����в�������
    # 2. ���row[1]��send��dss���ͣ���
    #    - ���վ��(node)�ǵ�һ����������: ��¼row[6]��ֵ����Ϊdecrement_value; row[6] = 0
    #    - ���վ��(node)���ǵ�һ����������row[6] -= decrement_value

    data_length = {
        'real_signal': [8, 4],
        'real': [4, 4],
        'int_signal': [4, 4],
        'bool_signal': [2, 2],
        'int': [2, 2],
        'bool': [1, 1],
        'device_signal': [4, 4]
    }
    # �½�һ��վ��node�б�
    node_list = []

    # ����һ����������ƫ�Ƶ�ַ�ĵݼ�ֵ
    # ����ʽ�����ݴ����У�ÿһ��node��������Сƫ�Ƶ�ַ���ḳ��decrement
    decrement = 0

    for row in data_list:
        # ��� direction �е������� send �� dss��dss��device signal��send�źţ�
        if row[1].lower() == 'send' or row[1].lower() == 'dss':
            # �ýڵ�ĵ�2�������һ��
            if row[0] in node_list:
                base_value = int(row[6]) - decrement
                row[6] = offset_gen(base_value, data_length[row[3]][1])
            # �ýڵ�ĵ�1��
            else:
                node_list.append(row[0])  # row[0]��node��
                decrement = int(row[6])   # row[6]�ǽڵ��һ�е�ԭoffset
                row[6] = 0                # ������offset��Ϊ0
        else:
            # ��ǰ����dsr��recv���͵ĵ㣬������offset�����Ұ�ԭ����ֵ��ԭ������ֵ�ģ������0
            row[6] = 0

    return data_list


def csv_handler(in_file_path, out_file_path):
    # file_name = os.listdir('./sheets')[2]
    # file_path = os.path.join(os.getcwd(), 'sheets', file_name)
    # new_file_path = os.path.join(os.getcwd(), 'sheets', 'new_' + file_name)

    with open(in_file_path, 'r', encoding='gbk') as csv_in, \
         open(out_file_path, 'w', encoding='gbk', newline='') as csv_out:


        reader = csv.reader(csv_in, delimiter=',')
        writer = csv.writer(csv_out, delimiter=',')

        # ����ļ���datalink�嵥
        if 'netdev' in in_file_path.lower():

            # ��дheader������title
            header = next(reader)
            # print(header)
            header[-1] = 'ƫ��'
            writer.writerow(header)

            # ����һ��������csv����list
            sorted_csv_list = sort_datalink(reader)
            # Ϊdatalink������������offset
            list_with_offset = datalink_offset_calc(sorted_csv_list)

        # ����ļ���firmnet�嵥
        elif 'download' in in_file_path.lower():

            # header����Ҫ����ֱ��д��writer��ȥ
            header = next(reader)
            writer.writerow(header)

            # ����Firmnet������Ҫ�󣬶����ݽ�������
            sorted_csv_list = sort_firmnet(reader)
            # Ϊfirmnet������������offset
            list_with_offset = firmnet_offset_calc(sorted_csv_list)

        else:
            list_with_offset = []

        # �����ɵ���������д��Ŀ���ļ�
        if list_with_offset:
            writer.writerows(list_with_offset)


def main():
    # �����ǰ�ļ����ڲ�����offset�ļ���
    # ���½��ļ���
    if not os.path.isdir('offset'):
        input('û�з��� offset �ļ��У���Ϊ���½���\n�뽫csv�ļ��������У������б�����\n��������˳�...')
        os.mkdir('offset')
        sys.exit(1)

    # ���������ļ����ڵ������ļ�
    # �����csv�ļ�����
    #   - ��������
    csvfiles = [item for item in os.listdir('./offset') if '.csv' == item[-4:].lower()]

    # ��offset�ļ�����û��csv�ļ�
    if len(csvfiles) == 0:
        input('��offset�ļ�����û�д�������ļ�����������˳�...')
        sys.exit(1)

    has_target = False
    for csvfile in csvfiles:
        if csvfile[:6].lower() == 'netdev' or csvfile[:8].lower() == 'download':
            has_target = True
            # print('\nDEBUG')
            # print(csvfile)
            in_file_path = os.path.join(os.getcwd(), 'offset', csvfile)
            out_file_path = os.path.join(os.getcwd(), 'offset', 'offset_' + csvfile)

            # ����csv_handler
            csv_handler(in_file_path, out_file_path)

            # ÿһ���ļ�������֮��hintһ���û�
            print(os.path.basename(csvfile) + ' �������')

    # ���û�������д��� netdev ���� download ���ļ���Ҫhintһ��
    if has_target:
        input('��������˳�...')
    else:
        input('�� offset �ļ�����û�� DEVNET �� DOWNLOAD ��� csv �ļ�����������˳�...')

if __name__ == '__main__':
    main()
