# offset
因为工作中的临时任务，需要对一些csv文件进行批量处理。

## 基本思路
### 偏移地址生成原则
1. datalink 的点，无论 send 还是 recv，都用规则直接计算。
2. firmnet 上的点，send 和 dss 用规则计算。recv 和 dsr，根据 send 和 dss 进行查找复制。
### 项目结构
1. 主要由两个`.py`文件组成
2. `offset.py`：基于EAST通信清单，计算偏移地址
3. `sync.py`：在EAST倒出的devnet.csv中，填写环网通信点的偏移地址

## 运行环境：
如果使用exe文件，则不需要任何相关环境。
如果使用.py脚本，则需要安装`python3`

## 用法
### 1. 文件准备
1. 在EAST中倒出四种类型的通信点: send, recv, dss, dsr。倒出文件名称为NETDEV_1.csv，其中`1`为站号。
2. 在EAST工程中找到四个环网的数据csv，名称形式为download.csv。按照以下对应关系，将文件重命名： ：
    - Safety System BUS：`download_1.csv`
    - Safety BUS Train A：`download_2.csv`
    - Safety BUS Train B：`download_3.csv`
    - HM Data BUS：`download_4.csv`

### 2. 生成偏移地址
1. 将以上所有的csv文件，放入 `/offset` 文件夹内
2. 执行命令：`$ python offset.py`（或双击可执行文件`offset.exe`）即可

### 3. 同步偏移地址
3. 将上一步生成的所有文件（以 "offset" 开头），放入 `/sync` 文件夹
4. 执行命令：`$ python sync.py`（或双击可执行文件`sync.exe`）即可
5. sync中生成的以 "synced" 开头的 csv 文件，是包含完整偏移地址的清单。（即本工具的最终结果）
6. 重要的使用前提：在sync功能中，四个环网文件的命名，必须严格按照`offset_download_1.csv`, `offset_download_2.csv`的方式。因为 sync 的代码中包含了对文件名中数字的功能性使用。`_1`代表Safety System BUS，`_2`带表Safety BUS TrainA，`_3`代表Safety BUS TrainB，`_4`代表HM Data BUS。


## 已知约束
1. 从 EAST 导出的 NETDEV.csv 文件，不可以使用 Excel 进行编辑和保存、保存。<br>**原因**：用 Excel 保存之后，csv 中原有的最一个逗号会被删除，导致文件处理过程中发生 list out of range 错误。（代码里使用了精确的行列关系进行csv文件操作）
2.

## TODO
1. 【DONE】~~`clear_folder.py`: 在编译exe的时候，会自动产生很多烦人的文件夹、文件。但真正想保留的只有`/dist`文件夹下的那个exe文件。所以写一个脚本，把没用的东西全都清除，只保留有价值的东西。~~
2. 【DONE】~~验证：~~
    - ~~代码计算出来的 datalink/recv 偏移量，和其对应的send值是否相等？~~
    - ~~查查环网中，一共有多少种数据类型(send, recv, dss?, dsr?)~~
3. 在等待文件处理时的stdout增加动画（完全是没有用的feature）