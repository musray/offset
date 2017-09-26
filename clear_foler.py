#!/usr/bin/env python3
import os
import shutil
import fnmatch


def main():
    root = os.getcwd()

    try:
        print('删除 __pycache__ 文件夹')
        shutil.rmtree(os.path.join(root, '__pycache__'))

        # TODO 如果找到exe_file，要把当前root内的同名exe_file删掉
        # exe_file = fnmatch.filter(os.listdir('./dist'), '*.exe')[0]
        # exe_file_path = os.path.join(root, 'dist', exe_file)
        # print('将可执行文件 %s 移动至根目录' % exe_file)
        # shutil.move(exe_file_path, '.')

        # print('删除 dist 文件夹')
        # shutil.rmtree(os.path.join(root, 'dist'))

        print('删除 build 文件夹')
        shutil.rmtree(os.path.join(root, 'build'))

        print('删除 .spec 文件')
        for name in os.listdir('.'):
            if fnmatch.fnmatch(name, '*.spec'):
                os.remove(name)

    except FileNotFoundError as e:
        print(e)

if __name__ == '__main__':
    main()
