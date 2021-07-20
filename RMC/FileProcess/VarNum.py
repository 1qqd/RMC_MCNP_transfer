import re
import RMC.FileProcess.Base as FB


class VarNum:
    def __init__(self, inp):
        self.file_name = inp
        self.content = ''
        self.varlist = []

    def repvar(self):
        self._read_in()
        print(' replacing variables...')
        _startindex = 0  # _startindex为查找新定义变量时使用
        '''
        变量代换思路：
        1. 从头开始查找一个变量定义
        2. 找到一个变量定义后，查找其是否重复定义；若没有找到变量定义，则退出
        3. 若重复定义，则将第一次定义到第二次定义之间的变量名用变量值代换，继续步骤2
        4. 若无重复定义，则将第一次定义到文档末尾之间的变量名用变量值代换，继续步骤1
        '''
        _find_var = True
        while _find_var:
            var = re.search(r'@(.*?)=[ ]*(.+?)[\n@/]', self.content[_startindex:], re.M | re.I)
            _find_var = var
            if var is None:
                break
            varname = ''.join(list(filter(None, var.group(1).split())))
            varvalue = ''.join(list(filter(None, var.group(2).split())))
            varvalue = varvalue.replace(' ', '')
            startindex = _startindex  # startindex为检查一个变量是否重复定义时使用

            if varname not in self.varlist:
                self.varlist.append(varname)
            else:
                '''
                已处理过的变量则跳过
                '''
                _startindex = var.span()[1] + _startindex
                continue

            while var:
                varlater = re.search('@[^=\na-zA-Z0-9_]*?' + varname + '[^=\na-zA-Z0-9_]*?=',
                                     self.content[var.span()[1] + startindex:], re.M | re.I)
                if varlater:
                    self.content = FB.Base.sub_string(self.content, [var.span()[1] + startindex,
                                                                     varlater.span()[0] + var.span()[1] + startindex],
                                                      varname, varvalue)
                else:
                    self.content = FB.Base.sub_string(self.content,
                                                      [var.span()[1] + startindex, len(list(self.content))], varname,
                                                      varvalue)
                startindex = startindex + var.span()[1]
                var = re.search('@[^=\na-zA-Z0-9_]*?' + varname + '[^=\na-zA-Z0-9_]*?=(.*?)[\n@/]', self.content[startindex:],
                                re.M | re.I)
                if var:
                    varvalue = ''.join(list(filter(None, var.group(1).split())))
                    varvalue = varvalue.replace(' ', '')

        print(' variable replacing finished.')
        self._write_file()

    def _read_in(self):
        with open(self.file_name, 'r') as f:
            self.content = f.read()

    def _write_file(self):
        with open(self.file_name, 'w+') as f:
            f.write(self.content)
