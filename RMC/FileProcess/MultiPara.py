import re
import os
import RMC.FileProcess.Base as FB
import itertools
import numpy as np
import shutil


class MultiPara:
    def __init__(self, filename):
        self.file_name = os.path.abspath(filename)
        self.content = ""
        self.paralist = []  # 变量表
        self.devided = []  # 依据各变量的划分方案，生成输入卡列表
        self.prioritynum = 90  # 若未指定展开次序，则从90开始编号
        self.prioritylist = []  # 各变量的优先序列号列表

    def _read_in(self):
        with open(self.file_name, 'r') as f:
            self.content = f.read()

    def _write_files(self):
        for i in range(len(self.devided)):
            with open('inp' + str(i + 1), 'w+') as f:
                f.write(self.devided[i])

    def devide(self):
        self._read_in()
        print('Analysing Multi-value variable ...')
        '''
        多重变量的处理思路：
        1. 处理 循环变量定义、三种快捷变量定义 的格式，将定义方式统一为基本定义格式，即 @ varname = {value1, value2, ..} # n 
        2. 构建多重变量表，包含 name, values, 展开次序
        3. 根据展开次序展开成各个方案，写入各个输入卡
        '''

        # 处理循环变量定义
        reg = r'{[^\{\n]*?([^\{\n,]+?:[^{\n]+?:[^\{\}\n,]+)[^\}\n]*?}'
        # 匹配 '{' + 尽量少的任意非{字符 + 尽量少的任意非{,字符 + ':' + 尽量少的任意非{字符 + ':' + 任意非{},字符 + 任意非}字符 + '}'
        searched = re.search(reg, self.content)
        while searched:
            cycle_str = searched.group(1).split(':')
            if len(cycle_str) == 3:
                # 如果是 start:end:internal 的类型
                startnum = float(cycle_str[0].replace(' ', ''))
                endnum = float(cycle_str[1].replace(' ', ''))
                internal = float(cycle_str[2].replace(' ', ''))
                input_check = (endnum - startnum) / internal
                if input_check - round(input_check) > 0.01:
                    # 检查 (endnum - startnum) / internal 是否为整数，不为整数则返回错误信息
                    print(' Multi-value variable ' + searched.group(1) + ' format error.')
                    return MultiState(False, True)
                numstr = np.linspace(startnum, endnum, round((endnum - startnum) / internal) + 1, endpoint=True)
                rep_str = ','.join(str(i) for i in numstr)
                self.content = FB.Base.replace_string(self.content, searched.span(1), rep_str)

            elif len(cycle_str) == 4:
                # 如果是 A:O:B:N 的类型
                para1 = float(cycle_str[0].replace(' ', ''))
                para2 = float(cycle_str[2].replace(' ', ''))
                oprator = cycle_str[1].replace(' ', '')
                cycle_num = int(cycle_str[3])
                if oprator == '+':
                    numstr = [para1]
                    for i in range(cycle_num):
                        numstr.append(para1 + (i + 1) * para2)
                elif oprator == '-':
                    numstr = [para1]
                    for i in range(cycle_num):
                        numstr.append(para1 - (i + 1) * para2)
                elif oprator == '*':
                    numstr = [para1]
                    for i in range(cycle_num):
                        numstr.append(para1 * pow(para2, (i + 1)))
                elif oprator == '/':
                    numstr = [para1]
                    for i in range(cycle_num):
                        numstr.append(para1 * pow((1 / para2), (i + 1)))
                else:
                    print(' A:O:B:N type, O only support +-*/')
                    return MultiState(False, True)
                rep_str = ','.join(str(i) for i in numstr)
                self.content = FB.Base.replace_string(self.content, searched.span(1), rep_str)
            else:
                # 不支持除了 start:end:internal 及 A:O:B:N 以外的循环定义方式
                print(' Multi-value variable format error.')
                return MultiState(False, True)

            searched = re.search(reg, self.content)

        self._remove_nosense_brace()  # 处理多余大括号

        # 处理快捷变量定义
        reg = r'{[^\}\{\n]*(\d+)[ ]*\*[ ]*([\d\.eE\+\-]+).*?}'
        # 匹配 '{' + 任意字符 + '整数' + '×' + 数字 + 其他字符 + '}'
        searched = re.search(reg, self.content)  # 形如{3*3}
        while searched:
            cycle_num = int(searched.group(1))
            rep_str = [searched.group(2)]
            for i in range(cycle_num - 1):
                rep_str.append(searched.group(2))
            rep_str = ','.join(rep_str)
            self.content = FB.Base.replace_string(self.content, [searched.span(1)[0], searched.span(2)[1]], rep_str)
            searched = re.search(reg, self.content)

        reg = r'{[^\}\{\n]*(\d+)[ ]*\*[ ]*{([^\}\{\n]+)}.*?}'
        # 匹配 '{' + 任意字符 + '整数' + '×' + '{' + 任意非{}字符 + '}' + 其他字符 + '}'
        searched = re.search(reg, self.content)  # 形如{3*{2,4}}
        while searched:
            cycle_num = int(searched.group(1))
            rep_str = [searched.group(2)]
            for i in range(cycle_num - 1):
                rep_str.append(searched.group(2))
            rep_str = ','.join(rep_str)
            self.content = FB.Base.replace_string(self.content, [searched.span(1)[0], searched.span(2)[1] + 1], rep_str)
            searched = re.search(reg, self.content)
            self._remove_nosense_brace()  # 处理多余大括号

        reg = r'(\d+)[ ]*\*[ ]*{([^\{\}\n]*)}'
        # 匹配 '整数' + '*' + '{' + 任意非{}字符 + '}'
        searched = re.search(reg, self.content)  # 形如3*{3，5}
        while searched:
            cycle_num = int(searched.group(1))
            rep_str = [searched.group(2)]
            for i in range(cycle_num - 1):
                rep_str.append(searched.group(2))
            rep_str = ','.join(rep_str)
            self.content = FB.Base.replace_string(self.content, searched.span(2), rep_str)
            self.content = FB.Base.replace_string(self.content, [searched.span(1)[0], searched.span(2)[0] - 1], '')
            searched = re.search(reg, self.content)
            self._remove_nosense_brace()  # 处理多余大括号

        # 构造多重变量表
        '''
        构造多重变量表处理方法：
        1. 搜索{}
        2. 判断paravalues个数，确定替换区间
        '''
        searched = re.search(r'{.*}', self.content)
        startindex = 0
        while searched:
            paravalues = searched.group()
            paravalues = re.sub('{', '', paravalues)
            paravalues = re.sub('}', '', paravalues)
            paravalues = re.sub(' ', '', paravalues)
            paravalues = list(filter(None, paravalues.split(',')))  # 变量值列表
            indexs = [i + startindex for i in list(searched.span())]  # 替换区间
            startindex = searched.span()[1] + startindex
            def_priority = re.match(r'[ ]*#[ ]*(\d+)', self.content[startindex:])  # 展开优先级
            if def_priority:
                # 如果定义了优先级，则使用用户定义的优先级
                self.content = FB.Base.replace_string(self.content, [x + startindex for x in def_priority.span()], '')
                self.paralist.append([paravalues, indexs, int(def_priority.group(1))])  # 将变量添加至变量列表
                if not self.prioritylist:
                    self.prioritylist.append([int(def_priority.group(1)), len(paravalues)])
                if int(def_priority.group(1)) not in np.array(self.prioritylist)[..., 0]:
                    self.prioritylist.append([int(def_priority.group(1)), len(paravalues)])
            else:
                # 若没有定义优先级，则使用系统预设优先级
                self.paralist.append([paravalues, indexs, self.prioritynum])
                self.prioritylist.append([self.prioritynum, len(paravalues)])
                self.prioritynum = self.prioritynum + 1
            searched = re.search('{.*}', self.content[startindex:])

        # 分解输入卡
        if len(self.paralist) > 0:
            print('Multi-value variable exists, splitting input files...')
            self.prioritylist = sorted(self.prioritylist, key=lambda x: x[0], reverse=True)

            _iterlist = []
            for _prinum, _valuenum in self.prioritylist:
                _iterlist.append(range(_valuenum))

            planindexs = list(itertools.product(*_iterlist))
            print('Total number of input files is' + str(len(planindexs)))  # 方案总数

            totalplans = []
            for indexs in planindexs:
                plan = list(range(len(self.paralist)))
                for i in range(len(indexs)):
                    index = indexs[i]
                    for j in range(len(self.paralist)):
                        para = self.paralist[j]
                        if para[2] == self.prioritylist[i][0]:
                            plan[j] = para[0][index]
                totalplans.append(plan)

            for plan in totalplans:
                i = len(self.paralist)
                tempcontent = self.content
                for paravalue in reversed(plan):
                    tempcontent = FB.Base.replace_string(tempcontent, self.paralist[i - 1][1], paravalue)
                    i = i - 1
                self.devided.append(tempcontent)

            if not os.path.exists(os.path.join(os.path.dirname(self.file_name), "MultiParainps")):
                os.mkdir(os.path.dirname(self.file_name) + "/MultiParainps")
            else:
                shutil.rmtree(os.path.dirname(self.file_name) + "/MultiParainps")
                os.mkdir(os.path.dirname(self.file_name) + "/MultiParainps")
            os.chdir(os.path.dirname(self.file_name) + "/MultiParainps")
            self._write_files()
            os.chdir(os.path.dirname(self.file_name))
            print("Multi-value variable analysing finished.\n")
            return MultiState(True)

        else:
            print('Multi-value variable does not exist. ')
            return MultiState(False)

    def _remove_nosense_brace(self):
        # 处理多余括号，例如{1,{2,3,4}}
        reg = r'{.*?,[^\*\n\{\},]*?{([^\*\n\{]*?)}.*?}'
        # 匹配 '{' + 尽量少的任意字符 + ',' + 不包含*,的字符 + '{' + 不包含*{的字符 + '}' + 任意字符 + '}'
        searched = re.search(reg, self.content)
        while searched:
            rep_str = searched.group(1)
            self.content = FB.Base.replace_string(self.content, [searched.span(1)[0] - 1, searched.span(1)[1] + 1],
                                                  rep_str)
            searched = re.search(reg, self.content)

        # 处理多余括号，例如{{1,2,3},4}
        reg = r'{[^\*\n\{\},]*?{([^\*\n\{]*?)}.*?}'
        # 匹配 '{' + 不包含*,{}的字符 + '{' + 不包含*{的字符 + '}' + 任意字符 + '}'
        searched = re.search(reg, self.content)
        while searched:
            rep_str = searched.group(1)
            self.content = FB.Base.replace_string(self.content, [searched.span(1)[0] - 1, searched.span(1)[1] + 1],
                                                  rep_str)
            searched = re.search(reg, self.content)


class MultiState:
    def __init__(self, processed, false_format=False):
        self._processed = processed
        self._false_format = false_format

    @property
    def processed(self):
        return self._processed

    @property
    def falseformat(self):
        return self._false_format
