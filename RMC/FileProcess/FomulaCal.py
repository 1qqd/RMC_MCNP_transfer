import re
import RMC.FileProcess.Base as FB
from numpy import *


class FomulaCal:
    def __init__(self, inp):
        self.file_name = inp
        self.content = ''

    def calfomula(self):
        self._read_in()

        print(' performing Formula calculating...')
        '''
        公式计算思路：
        循环查找[], 并调用python中的eval函数计算其中的内容
        '''
        fomula_find = re.search(r'\[([^\n\[]*?)\]', self.content)
        while fomula_find:
            indexs = fomula_find.span()
            self.content = FB.Base.replace_string(self.content, indexs, str(eval(fomula_find.group(1).lower())))
            fomula_find = re.search(r'\[([^\n\[]*?)\]', self.content)

        print(' Formula calculating finished')

        self._write_file()

    def _read_in(self):
        with open(self.file_name, 'r') as f:
            self.content = f.read()

    def _write_file(self):
        with open(self.file_name, 'w+') as f:
            f.write(self.content)
