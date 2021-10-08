MCNP to RMC转换工具
开发者：申鹏飞
邮箱：2043965149@qq.com

使用说明：
1. MCNPtoRMC.py 中提供了转换函数，可参考 runner.py 文件调用并处理。运行 runner.py 可以输入文件名，自动调用转换函数处理。支持‘？’和‘*’的通配输入（仅一次）。
其中，‘？’匹配单个字符，‘*’匹配任意字符
2. 针对每个输入的MCNP文件，会输出两个文件：一个是MCNP已解析部分的模型文件，会以 warning： 的形式提示未转换部分，请务必仔细阅读。
另一个是RMC解析输入文件。

注意：
1. MCNP的输入卡表示Cell和Surf的每一行 数字前 不能有空格（否则会转换失败）
2. 转换后需要手动设置RMC的lattice参数
提示：需注意设置MOVE和ROTATE参数，在表示lattice的Universe 和 该Universe填充的Cell 上均需设置（具体坐标原点转换要求请参考RMC的用户手册）

参考资料：
RMC用户手册在线版：https://rmc-doc.reallab.org.cn/en/latest/usersguide/index.html
