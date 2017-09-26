# offset
因为工作中的临时任务，需要对一些csv文件进行批量处理。

## 基本思路
### 偏移地址生成原则
1. datalink 的点，无论 send 还是 recv，都用规则直接计算。
2. firmnet 上的点，send 和 dss 用规则计算。recv 和 dsr，根据 send 和 dss 进行查找复制。

### 项目结构
1. 主要由两个`.py`文件组成
2. `offset.py`：基于EAST通信清单（ netdev 和 download ），计算偏移地址，并生成新文件。（offset 开头）
3. `sync.py`：将download中的环网偏移地址，同步到 netdev 中去，并生成新文件。（sync 开头）

## 运行环境：
如果使用exe文件，则不需要任何相关环境（推荐使用`pyinstaller`编译exe文件）。<br>
如果使用.py脚本，则需要安装`python3`。

## 用法
### 1. 文件准备
1. 在EAST中，以"站"为单位，分别导出四种类型的通信点: send, recv, dss, dsr。导出文件名称为NETDEV_1.csv，其中`1`为可变值，代表站号。
2. 在EAST工程文件夹内，找到四个环网的数据 download.csv。按照以下对应关系，将文件重命名：（命名必须严格，否则影响后续代码执行）
    - Safety System BUS：`download_1.csv`
    - Safety BUS Train A：`download_2.csv`
    - Safety BUS Train B：`download_3.csv`
    - HM Data BUS：`download_4.csv`

### 2. 生成偏移地址
1. 将以上所有的csv文件，放入 `/offset` 文件夹内。
2. 执行命令：`$ python offset.py`（或双击可执行文件`offset.exe`）即可。
3. 新生成文件，带有`offset`前缀。源文件内容保持不变。

### 3. 同步偏移地址
3. 将上一步生成的所有文件（以 "offset" 开头），放入 `/sync` 文件夹。
4. 执行命令：`$ python sync.py`（或双击可执行文件`sync.exe`）即可。
5. sync 中生成的 "sync" 开头 csv 文件，是包含完整偏移地址的清单。（即本工具的最终结果）


## 已知约束
1. 从 EAST 导出的 NETDEV.csv 文件，不可以使用 Excel 进行编辑和保存、保存。<br>**原因**：用 Excel 保存之后，csv 中原有的最一个逗号会被删除，导致文件处理过程中发生 list out of range 错误。（代码里使用了精确的行列关系进行csv文件操作）

## 开发相关
1. 如何生成exe文件? `$ pyinstaller offset.py --oneline`。
2. 生成的exe文件，保存在dist文件夹内。
2. `clear_folder.py`的作用？<br>即使使用 --oneline 选项，pyinstaller也会生成很多附加的文件或文件夹。<br>clear_folder.py脚本，在每次执行 pyinstaller 之后运行一次，用来清理没用的文件夹，仅保留dist文件夹。

## TODO
1. 【DONE】~~`clear_folder.py`: 在编译exe的时候，会自动产生很多烦人的文件夹、文件。但真正想保留的只有`/dist`文件夹下的那个exe文件。所以写一个脚本，把没用的东西全都清除，只保留有价值的东西。~~
2. 【DONE】~~验证：~~
    - ~~代码计算出来的 datalink/recv 偏移量，和其对应的send值是否相等？~~
    - ~~查查环网中，一共有多少种数据类型(send, recv, dss?, dsr?)~~
3. 在等待文件处理时的stdout增加动画（像是完全是没有用的feature）
4. ~~完成`clear_folder.py`~~
5. 如何确定netdev里的点，是netdev的点，还是datalink的点？2018-9-25
    - 当前的策略，对于netdev1-8（待确认）的表，Col[10]（K列）写了环网，就是环网。没写环网，就是datalink。
    - 对于9以后的表，全都是环网的点。
6. 如何确定是哪个环网？
    - 一共有四个环网，如何确定某个netdev中的点，是哪个环网上的？
    - 先给环网编号，分别是上层环网1号，SA是2号，SB是3号，HM是4号。
    - 初步：写一个死规则。比如netdev_1，都是1号环网上的点，netdev_12，都是2号环上的点。
    [solution]，可能要弄一个netdev和firmnet之间的同步关系图
7. 一个datalink的receive点，到底是从哪个站收到的？
    - 比如，RPC1，可能从RPC2，3，4都接收datalink的通信点
    - 再比如，ESF-A，可能从RPC1，2，3，4都接收通信点
    - 那么，如何从netdev表格中，判断一个recevie的datalink点的发送者是谁？
    [solution]可能需要弄一个netdev_*.csv各个文件之间的同步关系图
