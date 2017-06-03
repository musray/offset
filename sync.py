#!/usr/bin/env python3

# 这个文件用来同步Firmnet上Send和Receive的偏移地址
# 在Firmnet上，Send类型点的偏移地址，是手工指定的，
# 而Receive类型点的偏移地址，是从Send继承来的
# 手工继承（填写）的话太麻烦，还容易错，所以写了个脚本实现。


def main():
    # 基本思路
    # 用户把需要填写的csv（target），和已经填写好Send偏移地址的csv文件（source）放在同一文件夹内
    # 先open所有上述文件
    # 在需要填写offset的文件中，遍历所有行
    # 如果这一行是环网点、且点类型是Receive，那么:
    #   - 根据点名，在source中找对应点名，且校验找到的点是否为Send类型
    #   - 如果找到的点满足上条要求，则把source中的offset写入到target的相应位置上
    pass


if __name__ == '__main__':
    main()
