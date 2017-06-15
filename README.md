# offset
因为工作中的临时任务，需要对一些csv文件进行批量处理。

## 用法
1. 将待处理的csv文件，放入 `/offset` 文件夹内
2. `$ python offset.py` （在 DEVNET 和 download 文件中产生偏移地址）
3. 将上一步生成的文件（以 "offset" 开头），放入 `/sync` 文件夹
4. `$ python sync.py` (将 offset-download 中的 send 类型点的偏移地址，同步至 DEVNET 中)
5. sync中生成的以 "synced" 开头的 csv 文件，是包含完整偏移地址的清单。（即本工具的最终结果）


## 已知约束
约束：从 EAST 导出的 NETDEV.csv 文件，不可以使用 Excel 进行编辑和保存、保存。

原因：用 Excel 保存之后，csv 中原有的最一个逗号会被删除，导致文件处理过程中发生 list out of range 错误。（我在代码里使用了对各行的单元格操作）

## TODO
1. `clear_folder.py`: 在编译exe的时候，会自动产生很多烦人的文件夹、文件。但真正想保留的只有`/dist`文件夹下的那个exe文件。所以写一个脚本，把没用的东西全都清除，只保留有价值的东西。
2. 验证：
    - 代码计算出来的 datalink/recv 偏移量，和其对应的send值是否相等？
    - 查查环网中，一共有多少种数据类型(send, recv, dss?, dsr?)